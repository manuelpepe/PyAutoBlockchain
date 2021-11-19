// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.7.0 <0.9.0;

contract PABTest {
    address owner;
    bool myBool;
    uint8 myInt;
    string myString;

    constructor()
    {
        owner = msg.sender;
        myBool = true;
        myInt = 1;
        myString = "NEW";
    }

    function setOwner(address newOwner) public {
        /* require(msg.sender==owner, ...) missing on purpose */
        owner = newOwner;
    }

    function getOwner() public view returns(address) {
        return owner;
    }
        
    function setBool(bool newBool) public {
        myBool = newBool;
    }

    function getBool() public view returns(bool) {
        return myBool;
    }
        
    function setString(string memory newString) public {
        myString = newString;
    }

    function getString() public view returns(string memory) {
        return myString;
    }
        
    function setInt(uint8 newInt) public {
        myInt = newInt;
    }

    function getInt() public view returns(uint8) {
        return myInt;
    }

    function onlyOwnerCanGetThis() public view returns(string memory) {
        require(msg.sender==owner,"Not the owner");
        return "You are the owner";
    }
    
}