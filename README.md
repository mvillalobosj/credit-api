# credit-api

## Requirements
The following must be installed on the host machine:
* docker
* docker-compose
* make


## Usage

### Building Images
`make build`
* builds the necessary images defined in the docker-compose.yaml file

### Running Unit Tests
`make test_unit`
* runs all tests in the `tests/unit` folder

### Running API
`make run`

* if not already running, starts up the postgres container
* applies migrations in the `/migrations/versions` folder to the postgres instance using alembic
* starts the api (api will be running on `localhost:5001`)

### Running Functional Tests
(while API is running in separate terminal)
`make test_functional`
* runs all tests in the `tests/functional` folder

## API Specification
While running, the API can be hit on the host machine using `localhost:5001`

Full swagger API specification can be retrieved from `localhost:5001/swagger.json`

All numeric values (credit, payment amount, withdrawal, etc...) must be represented in microdollars. 1c = 1000000 microdollars. The values are stored and calculated in microdollars. This helps to prevent rounding errors when calculating in currencies.


### Testing
To test the endpoints manually, you can do the following:
1. Create a new customer and save its uuid
2. Create a new account with that customer uuid
3. Apply payments/withdrawals to that account using the account uuid. Specify different dates to simulate real user activity.
4. Check the account responses to ensure their accuracy

### Endpoints

#### /customer [POST]
* Creates a new customer and returns it back for confirmation.
##### Payload
```
{
    "fname": <Customer first name>,
    "lname": <Customer last name>,
    "email": <Customer email>
}
```

##### Response
```
{
    "uuid": <Customer uuid>,
    "fname": <Customer first name>,
    "lname": <Customer last name>,
    "email": <Customer email>
}
```
#### /customer/\<uuid\> [GET]
* `<uuid>` must be an existing customer id.
* Attempting to access a non-existing customer will return a 404.

##### Response:
```
{
    "uuid": <Customer uuid>,
    "fname": <Customer first name>,
    "lname": <Customer last name>,
    "email": <Customer email>
}
```

#### /account [POST]
* Creates a new account and returns it back for confirmation.
* All numeric values should be sent/received in microdollars

##### Payload
```
{
    "customerUUID": <The customer's UUID>,
    "maxCredit": <Maximum Credit for this account>,
    "timeOpened": <The time the account was opened>,
    "apr": <The apr for this credit line>
}
```
###### Response
```
{
    "uuid": <The account uuid>,
    "apr": <The account apr>,
    "maxCredit": <The maximum credit for this account>,
    "timeOpened": <The time the account was opened>,
    "availableCredit": <The amount of credit left on the account>,
    "principalOwed": <The amount of principal owed on the account>,
    "interestOwed": <The amount of interest owed on the account>
}
```

#### /account/\<uuid\>?time=\<time\>
* `<uuid>` is the account uuid
* `<time>` gets the account information as of a certain time. Defaults to now()
* Attempting to access a non-existing account will return a 404.

##### Response
```
{
    "uuid": <The account uuid>,
    "apr": <The account apr>,
    "maxCredit": <The maximum credit for this account>,
    "timeOpened": <The time the account was opened>,
    "availableCredit": <The amount of credit left on the account>,
    "principalOwed": <The amount of principal owed on the account>,
    "interestOwed": <The amount of interest owed on the account>
}
```

#### /account/payment [POST]
* Applies the payment then returns the updated balance information.
* Invalid payments will return a 422 error code.

##### Payload
```
{
    "accountUUID": <The account uuid>,
    "time": <The time the payment took place (default now())>,
    "amount": <The amount of the payment in microdollars>
}
```
##### Response
```
{
    "uuid": <The account uuid>,
    "apr": <The account apr>,
    "maxCredit": <The maximum credit for this account>,
    "timeOpened": <The time the account was opened>,
    "availableCredit": <The amount of credit left on the account>,
    "principalOwed": <The amount of principal owed on the account>,
    "interestOwed": <The amount of interest owed on the account>
}
```

#### /account/withdrawal [POST]
* Applies the withdrawal then returns the updated balance information.
* Invalid withdrawals will return a 422 error code.

##### Payload
```
{
    "accountUUID": <The account uuid>,
    "time": <The time the withdrawal took place (default now())>,
    "amount": <The amount of the withdrawal in microdollars>
}
```
##### Response
```
{
    "uuid": <The account uuid>,
    "apr": <The account apr>,
    "maxCredit": <The maximum credit for this account>,
    "timeOpened": <The time the account was opened>,
    "availableCredit": <The amount of credit left on the account>,
    "principalOwed": <The amount of principal owed on the account>,
    "interestOwed": <The amount of interest owed on the account>
}
```
