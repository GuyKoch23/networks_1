# Documentation
This documentation provides guidelines for implementing a client that can communicate with the provided server. Follow these steps to establish a connection and interact with the server.

---

## Table of Contents

1. [Overview](#overview)  
2. [Protocol](#protocol)  
3. [Supported Commands](#supported-commands)  
4. [Examples](#examples)  
5. [Error Handling](#error-handling)  

---

## Overview

The server provides services that include user authentication and basic command execution. Communication occurs over a TCP connection using a text-based protocol. To interact with the server, your client must follow the specified protocol for login and command execution.

---

## Protocol

### Communication Flow

1. **Login Phase**:
   - The client must authenticate by sending a username and password.
   - Credentials are sent in the following format:
     - **Username**: `User: <username>`
     - **Password**: `Password: <password>`
   - If the login is successful, the server will reply with `Hi {username_of_user}, good to see you.` and grant access to execute commands. Otherwise, the server will reply with `Failed to login.` and the client must retry to login (starting from reentering his username in the right format).

2. **Command Phase**:
   - After successful login, the client can send commands in plain text. The server responds with results or error messages.

3. **Disconnection**:
   - To terminate the session, the client sends the `quit` command.

---

## Supported Commands

### 1. `calculate:`
Performs arithmetic calculations.

- **Format**:  
  ```
  calculate: <num1> <operator> <num2>
  ```
- **Operators**: `+`, `-`, `*`, `/`, `^`
- **Example**:  
  ```
  calculate: 10 / 3
  ```
- **Response**:
The sever will send response in the format
  ```
  response: R.
  ```
  Note that in the case of division, the result is rounded to 2 digits after the decimal dot.
- **Error**:
  In case the result surpasses the limit values of signed int32, the server will respond with:
  ```
  error: result is too big
  ```
### 2. `max:`
Finds the maximum value in a list of numbers (there is not limit to the length of the list).

- **Format**:  
  ```
  max: (<num1> <num2> <num3> ...)
  ```
- **Example**:  
  ```
  max: (2 9 4 7)
  ```
- **Response**:
  The sever will send response in the format
  ```
  the maximum is Y
  ```

### 3. `factors:`
Returns the prime factors of a given number.

- **Format**:  
  ```
  factors: <number>
  ```
- **Example**:  
  ```
  factors: 28
  ```
- **Response**:
  The sever will send response in the format
  ```
  the prime factors of X are: p1, p2, … pn
  ```

### 4. `quit`
Ends the client session and disconnects from the server.

- **Format**:  
  ```
  quit
  ```

---

## Examples

### Login
#### Client:
```
User: alice
Password: mypassword123
```
#### Server:
```
Hi alice, good to see you.
```

### Calculate
#### Client:
```
calculate: 7 * 8
```
#### Server:
```
response: 56
```

### Max
#### Client:
```
max: (1 5 9 3)
```
#### Server:
```
the maximum is 9
```

### Factors
#### Client:
```
factors: 30
```
#### Server:
```
the prime factors of 30 are: 2, 3, 5
```

### Quit
#### Client:
```
quit
```
#### Server:
*(Connection terminates)*

---

## Error Handling

### General Errors
- Invalid commands or malformed messages will result in the server disconnecting the client.
  - Example:
    ```
    foo: bar
    ```
    Server response:
    ```
    Invalid command, disconnecting from socket
    ```

### Calculation Errors
- **Overflow**:
  ```
  error: result is too big
  ```
- **Invalid Input**:
  ```
  error: invalid calculation
  ```

### Authentication Errors
- Incorrect username or password:
  ```
  Failed to login.
  ```
  After this error, the client must retry to login (starting from reentering his username in the right format)