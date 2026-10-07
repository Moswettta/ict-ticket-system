ictApp.factory('AuthService', ['$http', '$window', function ($http, $window) {
    var API = '/api/auth';

    return {
        login: function (credentials) {
            return $http.post(API + '/login', credentials).then(function (res) {
                $window.localStorage.setItem('token', res.data.access_token);
                $window.localStorage.setItem('user', JSON.stringify(res.data.user));
                return res.data;
            });
        },
        register: function (data) {
            return $http.post(API + '/register', data);
        },
        logout: function () {
            $window.localStorage.removeItem('token');
            $window.localStorage.removeItem('user');
        },
        isLoggedIn: function () {
            return !!$window.localStorage.getItem('token');
        },
        getUser: function () {
            var u = $window.localStorage.getItem('user');
            return u ? JSON.parse(u) : null;
        },
        setUser: function (user) {
            $window.localStorage.setItem('user', JSON.stringify(user));
        },
        me: function () {
            return $http.get(API + '/me');
        }
    };
}]);
