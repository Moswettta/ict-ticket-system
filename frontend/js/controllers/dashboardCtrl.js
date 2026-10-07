ictApp.controller('DashboardCtrl', ['$scope', 'ApiService',
    function ($scope, ApiService) {
        var vm = this;
        vm.stats = {};
        vm.recentTickets = [];
        vm.expiring = [];

        function load() {
            ApiService.getStats().then(function (res) {
                vm.stats = res.data;
            });
            ApiService.getTickets().then(function (res) {
                vm.recentTickets = res.data.slice(0, 5);
            });
            if ($scope.main.user.role === 'admin' || $scope.main.user.role === 'it_staff') {
                ApiService.getExpiring().then(function (res) {
                    vm.expiring = res.data;
                });
            }
        }

        $scope.$on('viewChanged', function (e, view) {
            if (view === 'dashboard') load();
        });

        if ($scope.main.currentView === 'dashboard') {
            load();
        }

        $scope.dash = vm;
    }
]);
