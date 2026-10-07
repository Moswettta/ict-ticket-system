var ictApp = angular.module('ictApp', []);

// Initials filter for avatar
ictApp.filter('initials', function () {
    return function (name) {
        if (!name) return '?';
        var parts = name.trim().split(/\s+/);
        if (parts.length >= 2) {
            return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    };
});

// Status badge class helper
ictApp.filter('statusBadge', function () {
    return function (status) {
        return 'badge badge-' + (status || 'pending');
    };
});

// Date format
ictApp.filter('fmtDate', function () {
    return function (iso) {
        if (!iso) return '\u2014';
        var d = new Date(iso);
        return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    };
});

// Auth interceptor
ictApp.factory('authInterceptor', ['$q', '$window', function ($q, $window) {
    return {
        request: function (config) {
            var token = $window.localStorage.getItem('token');
            if (token) {
                config.headers = config.headers || {};
                config.headers.Authorization = 'Bearer ' + token;
            }
            return config;
        },
        responseError: function (rejection) {
            if (rejection.status === 401) {
                $window.localStorage.removeItem('token');
                $window.localStorage.removeItem('user');
                $window.location.reload();
            }
            return $q.reject(rejection);
        }
    };
}]);

ictApp.config(['$httpProvider', function ($httpProvider) {
    $httpProvider.interceptors.push('authInterceptor');
}]);
