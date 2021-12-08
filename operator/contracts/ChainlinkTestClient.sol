// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

import "@chainlink/contracts/src/v0.7/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.7/ConfirmedOwner.sol";

contract ChainlinkTestClient is ChainlinkClient, ConfirmedOwner {
  using Chainlink for Chainlink.Request;

  // ORACLE_PAYMENT is the amount of LINK tokens that this chainlink client contract
  // pays to the connected oracle operator contract
  // to do this this chainlink client contract needs to be adequatly funded with 
  // LINK tokens to successfully make any oracle requests
  // setting below: 0 link tokens sent -> no link funding needed
  uint256 constant private ORACLE_PAYMENT = 0; // 1 * LINK_DIVISIBILITY / 1000;
  uint256 public currentPrice;

  event LogLinkTokenAddressUpdated(
    address indexed link
  );

  event LogRequestEthereumPriceFulfilled(
    bytes32 indexed requestId,
    uint256 indexed price
  );

  // need to call 
  constructor() ConfirmedOwner(msg.sender){
    //setChainlinkToken(0xE2e73A1c69ecF83F464EFCE6A5be353a37cA09b2);
  }


  function requestEthereumPrice(address _oracle, string memory _jobId)
    public
    onlyOwner
  {
    Chainlink.Request memory req = buildChainlinkRequest(stringToBytes32(_jobId), address(this), this.fulfillEthereumPrice.selector);
    req.add("get", "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD");
    req.add("path", "USD");
    req.addInt("times", 100);
    sendChainlinkRequestTo(_oracle, req, ORACLE_PAYMENT);
  }

  function fulfillEthereumPrice(bytes32 _requestId, uint256 _price)
    public
    recordChainlinkFulfillment(_requestId)
  {
    emit LogRequestEthereumPriceFulfilled(_requestId, _price);
    currentPrice = _price;
  }

  function setLinkTokenAddress(address link) public onlyOwner {
    setChainlinkToken(link);
    emit LogLinkTokenAddressUpdated(link);
  }

  function getLinkTokenAddress() public view returns (address) {
    return chainlinkTokenAddress();
  }

  function withdrawLink() public onlyOwner {
    LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
    require(link.transfer(msg.sender, link.balanceOf(address(this))), "Unable to transfer");
  }

  function cancelRequest(
    bytes32 _requestId,
    uint256 _payment,
    bytes4 _callbackFunctionId,
    uint256 _expiration
  )
    public
    onlyOwner
  {
    cancelChainlinkRequest(_requestId, _payment, _callbackFunctionId, _expiration);
  }

  function stringToBytes32(string memory source) private pure returns (bytes32 result) {
    bytes memory tempEmptyStringTest = bytes(source);
    if (tempEmptyStringTest.length == 0) {
      return 0x0;
    }

    assembly { // solhint-disable-line no-inline-assembly
      result := mload(add(source, 32))
    }
  }
}