pragma solidity >=0.7.0 <0.9.0;

contract Controller {
    address public owner;

    mapping(address => uint8) public pools;
    uint8 lastPoolIndex;

    mapping(address => mapping(uint8 => uint8)) public balances;

    constructor() {
        owner = msg.sender;
        lastPoolIndex = 0;
    }

    function addPool(address token) public returns (uint8) {
        require(msg.sender == owner, "Only owner can add tokens");
        lastPoolIndex += 1;
        pools[token] = lastPoolIndex;
        return pools[token];
    }

    function getPoolId(address token) public view returns (uint8) {
        return pools[token];
    }

    function getBalance(address account, uint8 poolId)
        public
        view
        returns (uint8)
    {
        return balances[account][poolId];
    }

    function compound(uint8 poolId) public {
        require(balances[msg.sender][poolId] != 0, "Sender not staked in pool");
        balances[msg.sender][poolId] += 10;
    }

    function stake(uint8 poolId, uint8 amount) public {
        balances[msg.sender][poolId] += amount;
    }
}
