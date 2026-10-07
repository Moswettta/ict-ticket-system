ictApp.controller('MaintenanceCtrl', ['$scope', 'ApiService',
    function ($scope, ApiService) {
        var vm = this;
        vm.maintenances = [];
        vm.assets = [];
        vm.filterStatus = '';
        vm.showModal = false;
        vm.form = {};
        vm.message = null;

        function load() {
            var params = {};
            if (vm.filterStatus) params.status = vm.filterStatus;
            ApiService.getMaintenances(params).then(function (res) {
                vm.maintenances = res.data;
            });
        }

        function loadAssets() {
            ApiService.getAssets().then(function (res) {
                vm.assets = res.data;
            });
        }

        $scope.$on('viewChanged', function (e, view) {
            if (view === 'maintenance') {
                load();
                loadAssets();
            }
        });

        if ($scope.main.currentView === 'maintenance') {
            load();
            loadAssets();
        }

        vm.openCreate = function () {
            vm.form = {
                maintenance_type: 'preventive',
                scheduled_date: new Date().toISOString().slice(0, 10)
            };
            vm.showModal = true;
        };

        vm.save = function () {
            if (!vm.form.next_due_date && vm.form.scheduled_date) {
                var d = new Date(vm.form.scheduled_date);
                d.setMonth(d.getMonth() + 6);
                vm.form.next_due_date = d.toISOString().slice(0, 10);
            }
            ApiService.createMaintenance(vm.form).then(function () {
                vm.showModal = false;
                vm.message = 'Maintenance scheduled';
                load();
                $scope.main.loadExpiring();
            });
        };

        vm.markComplete = function (m) {
            var today = new Date().toISOString().slice(0, 10);
            var next = new Date();
            next.setMonth(next.getMonth() + 6);
            ApiService.updateMaintenance(m.id, {
                status: 'completed',
                completed_date: today,
                next_due_date: next.toISOString().slice(0, 10),
                performed_by: $scope.main.user.id
            }).then(function () {
                load();
                $scope.main.loadExpiring();
            });
        };

        vm.rowClass = function (m) {
            if (m.is_expired) return 'expiry-danger';
            if (m.days_until_due !== null && m.days_until_due <= 14) return 'expiry-warning';
            return '';
        };

        $scope.mnt = vm;
    }
]);
