ictApp.controller('MainCtrl', ['$scope', 'AuthService', 'ApiService',
    function ($scope, AuthService, ApiService) {
        var vm = this;

        vm.user = AuthService.getUser();
        vm.currentView = 'dashboard';
        vm.pageTitle = 'Dashboard';
        vm.sidebarCollapsed = false;
        vm.loading = false;
        vm.loginError = null;
        vm.regError = null;
        vm.regSuccess = null;
        vm.showRegister = false;
        vm.loginForm = {};
        vm.regForm = { role: 'user' };
        vm.expiringCount = 0;
        vm.selectedTicket = null;

        $scope.main = vm;

        vm.isLoggedIn = function () {
            return AuthService.isLoggedIn();
        };

        vm.roleColor = function () {
            if (!vm.user) return 'secondary';
            if (vm.user.role === 'admin') return 'danger';
            if (vm.user.role === 'it_staff') return 'warning';
            return 'primary';
        };

        vm.toggleSidebar = function () {
            vm.sidebarCollapsed = !vm.sidebarCollapsed;
        };

        vm.goTo = function (view, ticket) {
            vm.currentView = view;
            var titles = {
                'dashboard': 'Dashboard',
                'tickets': 'Tickets',
                'new-ticket': 'Create New Ticket',
                'assets': 'Assets / Workdesk',
                'maintenance': 'Preventive Maintenance',
                'users': 'User Management',
                'profile': 'My Profile',
                'ticket-detail': 'Ticket Details'
            };
            vm.pageTitle = titles[view] || view;
            if (ticket) {
                vm.selectedTicket = ticket;
            }
            $scope.$broadcast('viewChanged', view);
        };

        vm.login = function () {
            vm.loading = true;
            vm.loginError = null;
            AuthService.login(vm.loginForm).then(function (data) {
                vm.user = data.user;
                vm.currentView = 'dashboard';
                vm.pageTitle = 'Dashboard';
                vm.loadExpiring();
            }).catch(function (err) {
                vm.loginError = (err.data && err.data.error) || 'Login failed';
            }).finally(function () {
                vm.loading = false;
            });
        };

        vm.register = function () {
            vm.regError = null;
            vm.regSuccess = null;
            AuthService.register(vm.regForm).then(function () {
                vm.regSuccess = 'Account created! You can now login.';
                vm.regForm = { role: 'user' };
            }).catch(function (err) {
                vm.regError = (err.data && err.data.error) || 'Registration failed';
            });
        };

        vm.logout = function () {
            AuthService.logout();
            vm.user = null;
            vm.loginForm = {};
        };

        vm.loadExpiring = function () {
            if (!vm.isLoggedIn()) return;
            if (vm.user.role === 'admin' || vm.user.role === 'it_staff') {
                ApiService.getExpiring().then(function (res) {
                    vm.expiringCount = res.data.length;
                });
            }
        };

        if (vm.isLoggedIn()) {
            AuthService.me().then(function (res) {
                vm.user = res.data;
                AuthService.setUser(res.data);
                vm.loadExpiring();
            }).catch(function () {
                vm.logout();
            });
        }
    }
]);
