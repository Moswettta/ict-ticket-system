ictApp.controller('UsersCtrl', ['$scope', 'ApiService',
    function ($scope, ApiService) {
        var vm = this;
        vm.users = [];
        vm.showModal = false;
        vm.form = {};
        vm.message = null;

        function load() {
            ApiService.getUsers().then(function (res) {
                vm.users = res.data;
            });
        }

        $scope.$on('viewChanged', function (e, view) {
            if (view === 'users') load();
        });

        if ($scope.main.currentView === 'users') load();

        vm.openEdit = function (user) {
            vm.form = angular.copy(user);
            vm.form.password = '';
            vm.showModal = true;
        };

        vm.save = function () {
            var data = {
                full_name: vm.form.full_name,
                email: vm.form.email,
                department: vm.form.department,
                phone: vm.form.phone,
                role: vm.form.role,
                is_active: vm.form.is_active
            };
            if (vm.form.password) data.password = vm.form.password;
            ApiService.updateUser(vm.form.id, data).then(function () {
                vm.showModal = false;
                vm.message = 'User updated';
                load();
            });
        };

        $scope.usr = vm;
    }
]);
