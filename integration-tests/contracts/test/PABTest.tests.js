const PABTestArt = artifacts.require("PABTest");
contract('PABTest', (accounts) => {
    let PABTest;

    before(async () => {
        PABTest = await PABTestArt.deployed();
    })

    it('should get owner to account[0]', async () => {
        const owner = await PABTest.getOwner();
        assert.equal(owner, accounts[0]);
    });

    it('should set owner to account[1] from any account', async () => {
        await PABTest.setOwner(accounts[1], { from: accounts[2] });
        const owner = await PABTest.getOwner();
        assert.equal(owner, accounts[1]);
    });

    it('should set int', async () => {
        const firstInt = parseInt(await PABTest.getInt());
        await PABTest.setInt(firstInt + 123, { from: accounts[2] });
        const newInt = parseInt(await PABTest.getInt());
        assert.equal(newInt, firstInt + 123);
    });

    it('should set bool', async () => {
        const firstBool = !!await PABTest.getBool();
        await PABTest.setBool(!firstBool, { from: accounts[2] });
        const newBool = !!await PABTest.getBool();
        assert.notEqual(newBool, firstBool);
    });

    it('should set string', async () => {
        const newValue = "Some other string";
        const firstString = await PABTest.getString();
        await PABTest.setString(newValue, { from: accounts[2] });
        const newString = await PABTest.getString();
        assert.notEqual(newString, firstString);
        assert.equal(newString, newValue);
    });

});
