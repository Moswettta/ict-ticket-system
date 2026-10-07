ictApp.controller('ProfileCtrl', ['$scope', 'ApiService', 'AuthService',
    function ($scope, ApiService, AuthService) {
        var vm = this;
        vm.form = {};
        vm.message = null;
        vm.error = null;

        function load() {
            vm.form = angular.copy($scope.main.user);
            vm.form.password = '';
        }

        $scope.$on('viewChanged', function (e, view) {
            if (view === 'profile') load();
        });

        if ($scope.main.currentView === 'profile') load();

        vm.save = function () {
            vm.message = null;
            vm.error = null;
            var data = {
                full_name: vm.form.full_name,
                email: vm.form.email,
                department: vm.form.department,
                phone: vm.form.phone
            };
            if (vm.form.password) data.password = vm.form.password;

            ApiService.updateUser(vm.form.id, data).then(function (res) {
                vm.message = 'Profile updated successfully';
                $scope.main.user = res.data;
                AuthService.setUser(res.data);
                vm.form.password = '';
            }).catch(function (err) {
                vm.error = (err.data && err.data.error) || 'Update failed';
            });
        };

        $scope.prof = vm;
    }
]);
