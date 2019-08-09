pragma solidity ^0.5.0;

contract EventLog {
    uint64 public index = 0;
    event Log(uint64 indexed index, address indexed from, string content, uint256 date);
    
    function get_index() public view returns(uint64){
        return index;
    }

    function write(string memory content) public payable{
        index+=1;
        emit Log(index, msg.sender, content, now);
    }
}