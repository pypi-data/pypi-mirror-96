"""GraphQL endpoint for making queries to the Nautobot GraphQL endpoint."""
from typing import Optional, Dict, Iterable, Any


class GraphQLException(Exception):
    def __init__(self, graph_err):
        """GraphQL Exception handling.

        Args:
            response (Exception): Exception from the request 
        """
        self.json = graph_err.response.json()
        self.status_code = graph_err.response.status_code
        self.errors = graph_err.response.json()["errors"]
        self.url = graph_err.request.url
        self.body = graph_err.request.body
        self.reason = graph_err.response.reason

    def __str__(self):
        return str(self.errors)


class GraphQLRecord:
    def __init__(self, json: Dict[str, Any], status_code: int):
        """Initialization of class.

        Args:
            json (dict): The json response from making a graphql query.
            status_code (int): The HTTP status code from making the graphql query.
        """
        self.json = json
        self.status_code = status_code

    def __repr__(self):
        return f"GraphQLRecord(json={self.json}, status_code={self.status_code})"

    def __str__(self):
        return str(self.json)


class GraphQLQuery:
    def __init__(self, api):
        """Initialization of class.

        Args:
            api (pynautobot.api): pynatutobot Api class to make calls to the Nautobot API endpoints.
        """
        self.api = api
        # Add on top of the base_url the endpoint /graphql/ which will be the url used
        self.url = self.api.base_url + "/graphql/"

    def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> GraphQLRecord:
        """Runs query against Nautobot Graphql endpoint.

        Args:
            query (str): Query string to send to the API
            variables (dict): Dictionary of variables to use with the query string, defaults to None

        Raises:
            GraphQLException:
                - When the query string is invalid.
            TypeError:
                - When `query` passed in is not of type string.
                - When `variables` passed in is not a dictionary.
            Exception:
                - When unknown error is passed in, please open an issue so this can be addressed.

        Examples:
            >>> try:
            ...   response.raise_for_status()
            ... except Exception as e:
            ...   variable = e
            ... 
            >>> variable
            >>> variable.response.json()
            {'errors': [{'message': 'Cannot query field "nae" on type "DeviceType". Did you mean "name" or "face"?', 'locations': [{'line': 4, 'column': 5}]}]}

            >>> variable.response.status_code
            400

        Returns:
            GraphQLRecord: Response of the API call
        """
        # Check that the query data coming in is of a type of string
        if not isinstance(query, str):
            raise TypeError(f"Query should be of type string, not of type {type(query)}")

        # Check that variables coming in is a dictionary
        if variables is not None and not isinstance(variables, dict):
            raise TypeError(f"Variables should be of type dictionary, not of type {type(variables)}")

        payload = {"query": query, "variables": variables}

        response = self.api.http_session.post(self.url, json=payload, headers=self.api.headers)

        # Don't create an object with an error, raise an exception
        try:
            response.raise_for_status()
        except Exception as graph_err:
            if response.status_code == 400:
                raise GraphQLException(graph_err)
            else:
                raise graph_err

        return GraphQLRecord(json=response.json(), status_code=response.status_code)
