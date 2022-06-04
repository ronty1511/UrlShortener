# UrlShortener
Given an URL, this API generates a short URL with maximum 51 characters irrespective of the length of original request.

# Steps to deploy: 
1. Create a lambda function in AWS
2. Copy/paste the contents into lambda
3. Create db instance (RDS, for convenience)
4. Provide DB connection details in environment variables
5. Deploy lambda
6. Use function url/API gateway proxy integration to use from outside AWS
7. Pass URL as body through Postman in the following format: {'input_url': 'exampleurl.com'}
