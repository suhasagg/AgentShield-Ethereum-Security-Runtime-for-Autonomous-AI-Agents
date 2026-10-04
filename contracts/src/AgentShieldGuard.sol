// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IAIAgentAuthenticatedWallet.sol";

/// @notice Defense-in-depth guard for an ERC-4337/8196 integration.
/// @dev This reference contract binds execution to an owner-approved policy root,
/// target/value/action and one-time action digest. Production deployments should
/// compose the canonical ERC-8196 wallet/module and ERC-8126 verification adapter.
contract AgentShieldGuard {
    address public immutable owner;
    mapping(bytes32 => bool) public approvedPolicy;
    mapping(bytes32 => bool) public consumed;
    mapping(address => bool) public approvedTarget;
    uint256 public maxValuePerTx;

    event PolicyApproval(bytes32 indexed policyHash, bool approved);
    event TargetApproval(address indexed target, bool approved);
    event ActionConsumed(bytes32 indexed actionDigest, address indexed agent, address indexed target, uint256 value);

    modifier onlyOwner() {
        require(msg.sender == owner, "ONLY_OWNER");
        _;
    }

    constructor(address _owner, uint256 _maxValuePerTx) {
        require(_owner != address(0), "ZERO_OWNER");
        owner = _owner;
        maxValuePerTx = _maxValuePerTx;
    }

    function setPolicy(bytes32 policyHash, bool allowed) external onlyOwner {
        approvedPolicy[policyHash] = allowed;
        emit PolicyApproval(policyHash, allowed);
    }

    function setTarget(address target, bool allowed) external onlyOwner {
        approvedTarget[target] = allowed;
        emit TargetApproval(target, allowed);
    }

    function setMaxValue(uint256 value) external onlyOwner {
        maxValuePerTx = value;
    }

    function verifyAndConsume(
        IAIAgentAuthenticatedWallet.AgentAction calldata a
    ) external returns (bytes32 actionDigest) {
        require(approvedPolicy[a.policyHash], "POLICY_NOT_APPROVED");
        require(approvedTarget[a.target], "TARGET_NOT_APPROVED");
        require(a.value <= maxValuePerTx, "VALUE_LIMIT");
        require(block.timestamp <= a.validUntil, "ACTION_EXPIRED");
        actionDigest = keccak256(abi.encode(
            block.chainid, address(this), a.agent, a.action, a.target, a.value,
            keccak256(a.data), a.nonce, a.validUntil, a.policyHash, a.entropyCommitment
        ));
        require(!consumed[actionDigest], "REPLAY");
        consumed[actionDigest] = true;
        emit ActionConsumed(actionDigest, a.agent, a.target, a.value);
    }
}
