ictApp.controller('AssetsCtrl', ['$scope', 'ApiService',
    function ($scope, ApiService) {
        var vm = this;
        vm.assets = [];
        vm.users = [];
        vm.filterType = '';
        vm.filterStatus = '';
        vm.showModal = false;
        vm.showAssignModal = false;
        vm.editMode = false;
        vm.form = {};
        vm.selected = null;
        vm.assignUserId = '';
        vm.message = null;

        var types = ['laptop', 'printer', 'computer_parts', 'full_computer', 'monitor', 'other'];
        vm.assetTypes = types;

        function load() {
            var params = {};
            if (vm.filterType) params.type = vm.filterType;
            if (vm.filterStatus) params.status = vm.filterStatus;
            ApiService.getAssets(params).then(function (res) {
                vm.assets = res.data;
            });
        }

        function loadUsers() {
            ApiService.getUsers().then(function (res) {
                vm.users = res.data;
            });
        }

        $scope.$on('viewChanged', function (e, view) {
            if (view === 'assets') {
                load();
                loadUsers();
            }
        });

        if ($scope.main.currentView === 'assets') {
            load();
            loadUsers();
        }

        vm.openCreate = function () {
            vm.editMode = false;
            vm.form = { asset_type: 'laptop', status: 'available' };
            vm.showModal = true;
        };

        vm.openEdit = function (asset) {
            vm.editMode = true;
            vm.form = angular.copy(asset);
            vm.showModal = true;
        };

        vm.save = function () {
            var promise;
            if (vm.editMode) {
                promise = ApiService.updateAsset(vm.form.id, vm.form);
            } else {
                promise = ApiService.createAsset(vm.form);
            }
            promise.then(function () {
                vm.showModal = false;
                vm.message = 'Asset saved successfully';
                load();
            });
        };

        vm.openAssign = function (asset) {
            vm.selected = asset;
            vm.assignUserId = asset.assigned_to_user_id || '';
            vm.showAssignModal = true;
        };

        vm.submitAssign = function () {
            ApiService.assignAsset(vm.selected.id, {
                user_id: vm.assignUserId || null
            }).then(function () {
                vm.showAssignModal = false;
                load();
            });
        };

        $scope.ast = vm;
    }
]);
