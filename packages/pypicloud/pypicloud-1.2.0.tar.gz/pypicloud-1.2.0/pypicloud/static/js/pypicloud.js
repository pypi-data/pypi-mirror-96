/**
 * @format
 */
String.prototype.endsWith = function(suffix) {
  return this.indexOf(suffix, this.length - suffix.length) !== -1;
};

angular
  .module("pypicloud", [
    "ui.bootstrap",
    "ngRoute",
    "angularFileUpload",
    "ngCookies"
  ])
  .config([
    "$routeProvider",
    function($routeProvider) {
      $routeProvider.when("/", {
        templateUrl: STATIC + "partial/index.html",
        controller: "IndexCtrl"
      });

      $routeProvider.when("/package/:pkg", {
        templateUrl: STATIC + "partial/package.html",
        controller: "PackageCtrl"
      });

      $routeProvider.when("/new_admin", {
        templateUrl: STATIC + "partial/new_admin.html",
        controller: "NewAdminCtrl"
      });

      $routeProvider.when("/account", {
        templateUrl: STATIC + "partial/account.html",
        controller: "AccountCtrl"
      });

      $routeProvider.otherwise({
        redirectTo: "/"
      });
    }
  ])
  .config([
    "$compileProvider",
    function($compileProvider) {
      $compileProvider.directive("compileUnsafe", [
        "$compile",
        function($compile) {
          return function(scope, element, attrs) {
            scope.$watch(
              function(scope) {
                // watch the 'compile' expression for changes
                return scope.$eval(attrs.compileUnsafe);
              },
              function(value) {
                // when the 'compile' expression changes
                // assign it into the current DOM element
                element.html(value);

                // compile the new DOM and link it to the current
                // scope.
                $compile(element.contents())(scope);
              }
            );
          };
        }
      ]);
    }
  ])
  .directive("ngSetFocus", [
    "$timeout",
    function($timeout) {
      return function(scope, element, attrs) {
        scope.$watch(
          attrs.ngSetFocus,
          function(newValue) {
            if (newValue) {
              $timeout(function() {
                element[0].focus();
              });
            }
          },
          true
        );
      };
    }
  ])
  .run([
    "$rootScope",
    "$location",
    "$routeParams",
    function($rootScope, $location, $routeParams) {
      $rootScope.$on("$routeChangeSuccess", function(scope, current, pre) {
        $rootScope.location = {
          path: $location.path()
        };
      });
    }
  ])
  .filter("startFrom", function() {
    return function(input, start) {
      start = parseInt(start, 10);
      return input.slice(start);
    };
  })
  .directive("visible", [
    "$parse",
    function($parse) {
      return {
        restrict: "A",
        link: function(scope, element, attrs) {
          scope.$watch(
            function() {
              return $parse(attrs.visible)(scope);
            },
            function(visible) {
              element.css("visibility", visible ? "visible" : "hidden");
            }
          );
        }
      };
    }
  ])
  .controller("BaseCtrl", [
    "$rootScope",
    "$location",
    function($rootScope, $location) {
      $rootScope._ = _;
      $rootScope.USER = USER;
      $rootScope.ROOT = ROOT;
      $rootScope.DOWNLOAD_URL = DOWNLOAD_URL;
      $rootScope.API = ROOT + "api/";
      $rootScope.ADMIN = ROOT + "admin/";
      $rootScope.IS_ADMIN = IS_ADMIN;
      $rootScope.NEED_ADMIN = NEED_ADMIN;
      $rootScope.ACCESS_MUTABLE = ACCESS_MUTABLE;
      $rootScope.ALLOW_REGISTER = ALLOW_REGISTER;
      $rootScope.ALLOW_REGISTER_TOKEN = ALLOW_REGISTER_TOKEN;
      $rootScope.CAN_UPDATE_CACHE = CAN_UPDATE_CACHE;
      $rootScope.FALLBACK_URL = FALLBACK_URL;
      $rootScope.DEFAULT_READ = DEFAULT_READ;
      $rootScope.STATIC = STATIC;
      $rootScope.PARTIAL = STATIC + "partial/";
      $rootScope.VERSION = VERSION;
      $rootScope.SECURE_COOKIE = SECURE_COOKIE;
      $rootScope.ALLOW_DELETE = ALLOW_DELETE;
      if (NEED_ADMIN) {
        $location.path("/new_admin");
      }

      $rootScope.getDevice = function() {
        var envs = ["xs", "sm", "md", "lg"];

        var el = document.createElement("div");
        var body = document.getElementsByTagName("body")[0];
        body.appendChild(el);

        for (var i = envs.length - 1; i >= 0; i--) {
          var env = envs[i];

          el.setAttribute("class", "hidden-" + env);
          if (el.offsetWidth === 0 && el.offsetHeight === 0) {
            el.remove();
            return env;
          }
        }
      };

      $rootScope.device = $rootScope.getDevice();
      $rootScope.getWidth = function() {
        return window.innerWidth;
      };
      $rootScope.$watch($rootScope.getWidth, function(newValue, oldValue) {
        if (newValue != oldValue) {
          $rootScope.device = $rootScope.getDevice();
        }
      });
      window.onresize = function() {
        $rootScope.$apply();
      };
    }
  ])
  .controller("NavbarCtrl", [
    "$scope",
    function($scope) {
      $scope.navCollapsed = $scope.device === "xs";
      $scope.options = [];
    }
  ])
  .controller("IndexCtrl", [
    "$scope",
    "$http",
    "$location",
    "$cookies",
    function($scope, $http, $location, $cookies) {
      $scope.$cookies = $cookies;
      $scope.packages = null;
      $scope.pageSize = 10;
      $scope.maxSize = 8;
      $scope.currentPage = 1;
      $scope.uploadCollapsed = true;
      if (NEED_ADMIN) {
        $location.path("/new_admin");
      }

      $scope.showUpload = USER != null || _.contains(DEFAULT_WRITE, "everyone");

      var addPackages = function(packages) {
        var allNames = _.pluck($scope.packages, "name");
        var uniquePkgs = _.uniq(packages, false, function(pkg) {
          return pkg.name;
        });
        _.each(packages, function(pkg) {
          if (!_.contains(allNames, pkg.name)) {
            $scope.packages.push(pkg);
          }
        });
      };

      $scope.toggleUpload = function() {
        $scope.uploadCollapsed = !$scope.uploadCollapsed;
      };

      $http
        .get($scope.API + "package/", { params: { verbose: true } })
        .success(function(data, status, headers, config) {
          $scope.packages = data.packages;
        })
        .error(function(data, status, headers, config) {
          console.error("Fetching packages failed");
        });

      $scope.showPackage = function(pkg) {
        $location.path("/package/" + pkg);
      };

      $scope.uploadFinished = function(response) {
        addPackages([response]);
        $scope.uploadCollapsed = true;
      };

      $scope.closePipHelp = function() {
        $cookies.seenPipHelp = "true";
      };
    }
  ])
  .controller("LoginCtrl", [
    "$scope",
    "$http",
    "$window",
    "$location",
    function($scope, $http, $window, $location) {
      $scope.error = false;
      $scope.loggingIn = false;

      $scope.token = $location.search().token;
      if ($scope.token) {
        $scope.useToken = true;
        $scope.startWithToken = true;
      }
      if ($window.location.protocol != "https:" && SECURE_COOKIE) {
        $scope.secureCookieError = true;
      }

      $scope.toggleTokenRegistration = function() {
        $scope.useToken = !$scope.useToken;
      };

      $scope.submit = function(username, password) {
        $scope.loggingIn = true;
        var data = {
          username: username,
          password: password
        };
        $http
          .post(ROOT + "login", data)
          .success(function(data, status, headers, config) {
            $scope.loggingIn = false;
            $scope.error = false;
            $window.location = data.next;
          })
          .error(function(data, status, headers, config) {
            $scope.loggingIn = false;
            $scope.error = true;
            $scope.errorMsg = "Username or password invalid";
          });
      };

      $scope.register = function(username, password) {
        var data = {
          username: username,
          password: password
        };
        $http
          .put(ROOT + "login", data)
          .success(function(data, status, headers, config) {
            $scope.error = false;
            $scope.registered = username;
          })
          .error(function(data, status, headers, config) {
            $scope.error = true;
            if (status === 400) {
              $scope.errorMsg =
                data.message == null
                  ? "Error during registration"
                  : data.message;
            } else if (status === 403) {
              $scope.errorMsg = "Registration has been disabled";
            } else {
              $scope.errorMsg = "Error during registration: " + data.message;
            }
          });
      };

      $scope.tokenRegister = function(token, password) {
        var data = {
          token: token,
          password: password
        };
        $scope.registering = true;
        $http
          .put(ROOT + "tokenRegister", data)
          .success(function(data, status, headers, config) {
            $scope.error = false;
            $scope.registering = false;
            $window.location = data.next;
          })
          .error(function(data, status, headers, config) {
            $scope.error = true;
            $scope.registering = false;
            if (status === 400) {
              $scope.errorMsg =
                data.message == null
                  ? "Error during registration"
                  : data.message;
            } else {
              $scope.errorMsg = "Error during registration: " + data.message;
            }
          });
      };
    }
  ])
  .controller("PackageCtrl", [
    "$scope",
    "$http",
    "$route",
    "$fileUploader",
    function($scope, $http, $route, $fileUploader) {
      $scope.package_name = $route.current.params.pkg;
      $scope.showPreRelease = true;
      $scope.packages = null;
      $scope.pageSize = 10;
      $scope.maxSize = 8;
      $scope.currentPage = 1;

      $scope.filterPreRelease = function(pkg) {
        if ($scope.showPreRelease) {
          return true;
        }
        return pkg.version.match(/^\d+(\.\d+)*$/);
      };

      $http
        .get($scope.API + "package/" + $scope.package_name)
        .success(function(data, status, headers, config) {
          $scope.packages = data.packages;
          $scope.filtered = data.packages;
          $scope.can_write = data.write;
        })
        .error(function(data, status, headers, config) {
          console.error(
            "Fetching package list failed for:",
            $scope.package_name
          );
        });

      $scope.deletePackage = function(pkg) {
        var index = $scope.packages.indexOf(pkg);
        pkg.deleting = true;
        var data = {
          name: $scope.package_name
        };
        var url =
          $scope.API + "package/" + $scope.package_name + "/" + pkg.filename;
        $http({ method: "delete", url: url })
          .success(function(data, status, headers, config) {
            $scope.packages.splice(index, 1);
          })
          .error(function(data, status, headers, config) {
            pkg.deleting = false;
            alert("Error deleting package");
          });
      };

      $scope.uploadFinished = function(response) {
        $scope.packages.unshift(response);
        $scope.uploadCollapsed = true;
      };
    }
  ])
  .controller("UploadCtrl", [
    "$scope",
    "$fileUploader",
    function($scope, $fileUploader) {
      var uploader = ($scope.uploader = $fileUploader.create({
        scope: $scope,
        alias: "content"
      }));

      $scope.canUpload = function() {
        return uploader.queue.length === 1 && !$scope.uploading;
      };

      $scope.uploadPackage = function() {
        $scope.uploading = true;
        var item = uploader.queue[0];
        var filename = item.file.name;
        if ($scope.package_name) {
          item.url =
            $scope.API + "package/" + $scope.package_name + "/" + filename;
        } else {
          item.url = $scope.ROOT + "simple/";
        }
        item.upload();
      };

      uploader.bind("success", function(event, xhr, item, response) {
        uploader.clearQueue();
        $scope.uploading = false;
        if ($scope.uploadFinished !== undefined) {
          $scope.uploadFinished(response);
        }
      });

      uploader.bind("error", function(event, xhr, item, response) {
        $scope.uploading = false;
        alert("Error during upload! " + response);
      });
    }
  ])
  .controller("TableCtrl", [
    "$scope",
    "$sce",
    "$interpolate",
    function($scope, $sce, $interpolate) {
      $scope.currentPage = 1;
      $scope.searchable = false;
      $scope.searchStrict = false;
      $scope.pageSize = 10;
      $scope.maxSize = 8;
      $scope.items = [];
      $scope.columns = [];
      $scope.title = "";
      $scope.ordering = "toString()";
      $scope.rowClick = null;

      // For making the table mutable
      $scope.disableEdits = false;
      $scope.addItems = null;
      $scope.addCallback = null;
      $scope.deleteText = "Delete";
      $scope.deleteCallback = null;
      $scope.deleteButtonElement = null;

      // Set arguments from parent scope
      if (_.isObject($scope.tableArgs)) {
        _.each($scope.tableArgs, function(value, key) {
          $scope[key] = value;
        });
      }

      if ($scope.rowClick === null) {
        $scope.rowClick = function() {};
        $scope.clickable = false;
      } else {
        $scope.clickable = true;
      }

      // TODO: put a scope.watch() on tableArgs

      $scope.compile = function(html, item) {
        return $sce.trustAsHtml($interpolate(html)({ item: item }));
      };

      $scope.toggleShowAdd = function() {
        $scope.showAdd = !$scope.showAdd;
        if (!$scope.showAdd) {
          $scope.newItem = "";
          $scope.errorMsg = undefined;
          $scope.showAdd = false;
        }
      };

      $scope.addItem = function() {
        $scope.errorMsg = $scope.addCallback($scope.newItem);
        if ($scope.errorMsg === undefined) {
          $scope.newItem = "";
        }
      };
    }
  ])
  .controller("NewAdminCtrl", [
    "$scope",
    "$http",
    "$location",
    function($scope, $http, $location) {
      $scope.register = function(username, password) {
        var data = {
          username: username,
          password: password
        };
        $http
          .put(ROOT + "login", data)
          .success(function(data, status, headers, config) {
            window.location = ROOT;
          })
          .error(function(data, status, headers, config) {
            alert("Error registering admin user");
          });
      };
    }
  ])
  .controller("AccountCtrl", [
    "$scope",
    "$http",
    function($scope, $http) {
      $scope.changePassword = function(oldPassword, newPassword) {
        if (
          !oldPassword ||
          !newPassword ||
          oldPassword.length === 0 ||
          newPassword.length === 0
        ) {
          $scope.passError = "Password cannot be blank!";
          return;
        }
        var data = {
          new_password: newPassword,
          old_password: oldPassword
        };
        $scope.changingPasswordNetwork = true;
        $http
          .post($scope.API + "user/password", data)
          .success(function(data, status, headers, config) {
            $scope.changingPasswordNetwork = false;
            $scope.changingPassword = false;
            $scope.newPassword = "";
            $scope.oldPassword = "";
            $scope.passError = null;
          })
          .error(function(data, status, headers, config) {
            $scope.changingPasswordNetwork = false;
            $scope.passError = "Invalid password!";
          });
      };
    }
  ]);
