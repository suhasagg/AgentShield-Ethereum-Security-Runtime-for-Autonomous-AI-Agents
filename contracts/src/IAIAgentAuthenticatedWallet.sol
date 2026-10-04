// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.20;

/// Minimal interoperability surface inspired by ERC-8196.
/// Consult the canonical ERC for production conformance.
interface IAIAgentAuthenticatedWallet {
    struct AgentAction {
        address agent;
        string action;
        address target;
        uint256 value;
        bytes data;
        uint256 nonce;
        uint256 validUntil;
        bytes32 policyHash;
        bytes32 entropyCommitment;
    }
    function executeAgentAction(
        AgentAction calldata agentAction,
        bytes calldata agentSignature,
        bytes calldata verificationProof
    ) external returns (bytes memory);
}
