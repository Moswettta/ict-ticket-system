ictApp.factory('ApiService', ['$http', function ($http) {
    return {
        getTickets: function (params) {
            return $http.get('/api/tickets', { params: params || {} });
        },
        getTicket: function (id) {
            return $http.get('/api/tickets/' + id);
        },
        createTicket: function (data) {
            return $http.post('/api/tickets', data);
        },
        updateTicket: function (id, data) {
            return $http.put('/api/tickets/' + id, data);
        },
        approveTicket: function (id, data) {
            return $http.post('/api/tickets/' + id + '/approve', data);
        },
        assignTicket: function (id, data) {
            return $http.post('/api/tickets/' + id + '/assign', data);
        },
        getAssets: function (params) {
            return $http.get('/api/assets', { params: params || {} });
        },
        createAsset: function (data) {
            return $http.post('/api/assets', data);
        },
        updateAsset: function (id, data) {
            return $http.put('/api/assets/' + id, data);
        },
        assignAsset: function (id, data) {
            return $http.post('/api/assets/' + id + '/assign', data);
        },
        getMaintenances: function (params) {
            return $http.get('/api/maintenances', { params: params || {} });
        },
        getExpiring: function () {
            return $http.get('/api/maintenances/expiring');
        },
        createMaintenance: function (data) {
            return $http.post('/api/maintenances', data);
        },
        updateMaintenance: function (id, data) {
            return $http.put('/api/maintenances/' + id, data);
        },
        getUsers: function () {
            return $http.get('/api/users');
        },
        getUser: function (id) {
            return $http.get('/api/users/' + id);
        },
        updateUser: function (id, data) {
            return $http.put('/api/users/' + id, data);
        },
        getStats: function () {
            return $http.get('/api/dashboard/stats');
        }
    };
}]);
