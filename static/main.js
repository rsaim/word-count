(function () {
    'use strict';

    angular.module('WordcountApp', [])

        .controller('WordcountController', ['$scope', '$log', '$http', '$timeout',
            function ($scope, $log, $http, $timeout) {

                $scope.getResults = function () {

                    var url_input = $scope.url_input;

                    $log.log("Making the post request for " + url_input);

                    // Start the API request.
                    $http.post('/start', {'url': url_input}).
                    success(function (results) {
                        $log.log("SUCCESS submitted request. ID: " + results);
                        $log.log("Starting polling");
                        getWordCount(results);
                    }).error(function (error) {
                        $log.log("ERROR: " + error);
                    })
                };

                function getWordCount(jobID) {

                    var timeout = "";

                    var poller = function () {
                        // fire another request
                        $http.get('/results/' + jobID).
                        success(
                            function (data, status, headers, config) {
                                if (status === 202) {
                                    $log.log(data, status);
                                } else if (status === 200) {
                                    $log.log(data);
                                    $scope.wordcounts = data;
                                    $timeout.cancel(timeout);
                                    return false;
                                }
                                $log.log("Polling for 2s")
                                timeout = $timeout(poller, 2000);
                            }).
                        error(function (error) {
                            $log.log("ERROR: " + error)
                        });
                    };
                    poller();
                }
            }
        ]);
}());