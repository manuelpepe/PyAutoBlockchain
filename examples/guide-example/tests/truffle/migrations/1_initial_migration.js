const Controller = artifacts.require("Controller");
const Token = artifacts.require("Token");

module.exports = async function (deployer) {
  await deployer.deploy(Controller);
  await deployer.deploy(Token);

  let accounts = await web3.eth.getAccounts();
  let owner = accounts[0];

  let IToken = await Token.deployed();
  let IController = await Controller.deployed();

  await IController.addPool(IToken.address, { from: owner });
};
