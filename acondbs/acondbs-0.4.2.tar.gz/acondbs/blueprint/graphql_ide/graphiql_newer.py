
##__________________________________________________________________||
# Based on https://github.com/graphql/graphiql/blob/codemirror-graphql@1.0.0/examples/graphiql-cdn/index.html
# To obtain fetchURL, inserted the lines https://github.com/graphql-python/flask-graphql/blob/v2.0.1/flask_graphql/render_graphiql.py#L33-L64
GRAPHIQL_NEWER = '''<!--
 *  Copyright (c) 2021 GraphQL Contributors
 *  All rights reserved.
 *
 *  This source code is licensed under the license found in the
 *  LICENSE file in the root directory of this source tree.
-->
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        height: 100%;
        margin: 0;
        width: 100%;
        overflow: hidden;
      }

      #graphiql {
        height: 100vh;
      }
    </style>

    <!--
      This GraphiQL example depends on Promise and fetch, which are available in
      modern browsers, but can be "polyfilled" for older browsers.
      GraphiQL itself depends on React DOM.
      If you do not want to rely on a CDN, you can host these files locally or
      include them directly in your favored resource bunder.
    -->
    <script
      crossorigin
      src="https://unpkg.com/react@16/umd/react.development.js"
    ></script>
    <script
      crossorigin
      src="https://unpkg.com/react-dom@16/umd/react-dom.development.js"
    ></script>

    <!--
      These two files can be found in the npm module, however you may wish to
      copy them directly into your environment, or perhaps include them in your
      favored resource bundler.
     -->
    <link rel="stylesheet" href="https://unpkg.com/graphiql/graphiql.min.css" />
  </head>

  <body>
    <div id="graphiql">Loading...</div>
    <script
      src="https://unpkg.com/graphiql/graphiql.min.js"
      type="application/javascript"
    ></script>
    <script src="/renderExample.js" type="application/javascript"></script>
    <script>
      // Collect the URL parameters
      var parameters = {};
      window.location.search.substr(1).split('&').forEach(function (entry) {
        var eq = entry.indexOf('=');
        if (eq >= 0) {
          parameters[decodeURIComponent(entry.slice(0, eq))] =
            decodeURIComponent(entry.slice(eq + 1));
        }
      });

      // Produce a Location query string from a parameter object.
      function locationQuery(params) {
        return '?' + Object.keys(params).map(function (key) {
          return encodeURIComponent(key) + '=' +
            encodeURIComponent(params[key]);
        }).join('&');
      }

      // Derive a fetch URL from the current URL, sans the GraphQL parameters.
      var graphqlParamNames = {
        query: true,
        variables: true,
        operationName: true
      };

      var otherParams = {};
      for (var k in parameters) {
        if (parameters.hasOwnProperty(k) && graphqlParamNames[k] !== true) {
          otherParams[k] = parameters[k];
        }
      }
      var fetchURL = locationQuery(otherParams);


      function graphQLFetcher(graphQLParams) {
        return fetch(
          fetchURL,
          {
            method: 'post',
            headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(graphQLParams),
            credentials: 'omit',
          },
        ).then(function (response) {
          return response.json().catch(function () {
            return response.text();
          });
        });
      }

      ReactDOM.render(
        React.createElement(GraphiQL, {
          fetcher: graphQLFetcher,
          defaultVariableEditorOpen: true,
        }),
        document.getElementById('graphiql'),
      );
    </script>
  </body>
</html>'''

##__________________________________________________________________||
