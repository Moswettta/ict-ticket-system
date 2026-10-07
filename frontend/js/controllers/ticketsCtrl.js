ictApp.controller('TicketsCtrl', ['$scope', 'ApiService',
    function ($scope, ApiService) {
        var vm = this;
        vm.tickets = [];
        vm.filterStatus = '';
        vm.users = [];
        vm.assets = [];
        vm.showAssignModal = false;
        vm.showApproveModal = false;
        vm.selected = null;
        vm.assignForm = {};
        vm.approveForm = { action: 'approve', notes: '' };
        vm.newTicket = { priority: 'medium', category: 'hardware' };
        vm.message = null;
        vm.error = null;

        function load() {
            var params = {};
            if (vm.filterStatus) params.status = vm.filterStatus;
            ApiService.getTickets(params).then(function (res) {
                vm.tickets = res.data;
            });
        }

        function loadLookups() {
            if ($scope.main.user.role === 'admin' || $scope.main.user.role === 'it_staff') {
                ApiService.getUsers().then(function (res) {
                    vm.users = res.data.filter(function (u) {
                        return u.role === 'it_staff' || u.role === 'admin';
                    });
                });
                ApiService.getAssets().then(function (res) {
                    vm.assets = res.data;
                });
            }
        }

        $scope.$on('viewChanged', function (e, view) {
            if (view === 'tickets' || view === 'new-ticket' || view === 'ticket-detail') {
                load();
                loadLookups();
            }
        });

        if (['tickets', 'new-ticket', 'ticket-detail'].indexOf($scope.main.currentView) >= 0) {
            load();
            loadLookups();
        }

        vm.setFilter = function (status) {
            vm.filterStatus = status;
            load();
        };

        vm.openDetail = function (ticket) {
            $scope.main.goTo('ticket-detail', ticket);
        };

        vm.createTicket = function () {
            vm.error = null;
            vm.message = null;
            ApiService.createTicket(vm.newTicket).then(function () {
                vm.message = 'Ticket submitted successfully!';
                vm.newTicket = { priority: 'medium', category: 'hardware' };
                setTimeout(function () {
                    $scope.main.goTo('tickets');
                    $scope.$apply();
                }, 1200);
            }).catch(function (err) {
                vm.error = (err.data && err.data.error) || 'Failed to create ticket';
            });
        };

        vm.openApprove = function (ticket) {
            vm.selected = ticket;
            vm.approveForm = { action: 'approve', notes: '' };
            vm.showApproveModal = true;
        };

        vm.submitApprove = function () {
            ApiService.approveTicket(vm.selected.id, vm.approveForm).then(function (res) {
                vm.showApproveModal = false;
                load();
                if ($scope.main.selectedTicket && $scope.main.selectedTicket.id === res.data.id) {
                    $scope.main.selectedTicket = res.data;
                }
            });
        };

        vm.openAssign = function (ticket) {
            vm.selected = ticket;
            vm.assignForm = {
                assigned_to: ticket.assigned_to || '',
                asset_id: ticket.asset_id || '',
                status: ticket.status === 'approved' ? 'in_progress' : ticket.status
            };
            vm.showAssignModal = true;
        };

        vm.submitAssign = function () {
            var data = angular.copy(vm.assignForm);
            if (data.assigned_to === '') data.assigned_to = null;
            if (data.asset_id === '') data.asset_id = null;
            ApiService.assignTicket(vm.selected.id, data).then(function (res) {
                vm.showAssignModal = false;
                load();
                if ($scope.main.selectedTicket && $scope.main.selectedTicket.id === res.data.id) {
                    $scope.main.selectedTicket = res.data;
                }
            });
        };

        vm.resolveTicket = function (ticket, notes) {
            ApiService.assignTicket(ticket.id, {
                status: 'resolved',
                resolution_notes: notes || 'Resolved'
            }).then(function () {
                load();
            });
        };

        $scope.tix = vm;
    }
]);
