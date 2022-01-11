pragma solidity >=0.7.0 <0.9.0;

contract Token {
    /* For tests the only thing needed of this contract is the address */
    address public owner;

    constructor() {
        owner = msg.sender;
    }
}
