const ControllerArt = artifacts.require("Controller");
const TokenArt = artifacts.require("Token");

contract('Controller', (accounts) => {
    let Controller;
    let Token;
    let owner;

    before(async () => {
        Controller = await ControllerArt.deployed();
        Token = await TokenArt.deployed();
        owner = accounts[0];
    })

    it('should get owner to account[0]', async () => {
        assert.equal(await Controller.owner(), owner);
        assert.equal(await Token.owner(), owner);
    });

    it('should add firsttoken to pools as ID 1', async () => {
        await Controller.addPool(Token.address, { from: owner });
        const pooldId = await Controller.pools(Token.address);
        assert.equal(pooldId, 1);
    });

    it('should add 10 on compound', async () => {
        const poolId = await Controller.pools(Token.address);
        assert.equal(await Controller.getBalance(owner, poolId), 0);
        await Controller.stake(poolId, 10, { from: owner });
        assert.equal(await Controller.getBalance(owner, poolId), 10);
        await Controller.compound(poolId, { from: owner });
        assert.equal(await Controller.getBalance(owner, poolId), 20);
    });
});
