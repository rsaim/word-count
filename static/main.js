(function () {
    'use strict';

    angular.module('WordcountApp', [])

        .controller('WordcountController', ['$scope', '$log', '$http', '$timeout',

            function ($scope, $log, $http, $timeout) {

                $scope.submitButtonText = "Submit";
                $scope.loading = false;
                $scope.urlError = false;
                $log.log($scope.urlError);

                $scope.getResults = function () {

                    var url_input = $scope.url_input;

                    $log.log("Making the post request for " + url_input);

                    // Start the API request.
                    $http.post('/start', {'url': url_input}).
                    success(function (results) {
                        $scope.urlError = false;
                        $log.log("SUCCESS submitted request. ID: " + results);
                        $log.log("Starting polling");
                        getWordCount(results);
                        $scope.wordcounts = null;
                        $scope.loading = true;
                        $scope.submitButtonText = "Loading...";
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
                                    $scope.loading = false;
                                    $scope.submitButtonText = "Submit";
                                    $timeout.cancel(timeout);
                                    return false;
                                }
                                $log.log("Polling for 2s")
                                timeout = $timeout(poller, 2000);
                            }).
                        error(function (error) {
                            $log.log("ERROR: " + error);
                            $scope.loading = false;
                            $scope.submitButtonText = "Submit";
                            $scope.urlError = true;
                        });
                    };
                    poller();
                }
            }
        ])

        .directive('wordCountChart', ['$parse', function ($parse) {
        return {
          restrict: 'E',
          replace: true,
          template: '<div id="chart"></div>',
          link: function (scope) {
            scope.$watch('wordcounts', function() {
              d3.select('#chart').selectAll('*').remove();
              var data = scope.wordcounts;
              for (var word in data) {
                var key = data[word][0];
                var value = data[word][1];
                d3.select('#chart')
                  .append('div')
                  .selectAll('div')
                  .data(word)
                  .enter()
                  .append('div')
                  .style('width', function() {
                    return (value * 15) + 'px';
                  })
                  .text(function(d){
                    return key;
                  });
              }
            }, true);
          }
         };
      }]);

}());