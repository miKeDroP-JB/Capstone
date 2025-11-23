// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title OrbNFT
 * @dev NFT contract for 0RB_AETHER ecosystem
 * Supports music, art, and content NFTs with built-in royalties
 */
contract OrbNFT is ERC721URIStorage, ERC721Royalty, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    enum NFTType { MUSIC, ART, CONTENT, GAMING }

    struct NFTMetadata {
        NFTType nftType;
        address creator;
        uint256 createdAt;
        string category;
    }

    mapping(uint256 => NFTMetadata) public tokenMetadata;
    mapping(address => uint256[]) public creatorTokens;

    event NFTMinted(
        uint256 indexed tokenId,
        address indexed creator,
        NFTType nftType,
        string uri
    );

    constructor() ERC721("0RB NFT", "ORB") Ownable(msg.sender) {}

    /**
     * @dev Mint new NFT with royalty info
     * @param to Recipient address
     * @param uri Metadata URI (IPFS/Arweave)
     * @param nftType Type of NFT
     * @param category Custom category string
     * @param royaltyReceiver Address to receive royalties
     * @param royaltyFee Royalty fee in basis points (e.g., 500 = 5%)
     */
    function mint(
        address to,
        string memory uri,
        NFTType nftType,
        string memory category,
        address royaltyReceiver,
        uint96 royaltyFee
    ) public returns (uint256) {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();

        _safeMint(to, newTokenId);
        _setTokenURI(newTokenId, uri);
        _setTokenRoyalty(newTokenId, royaltyReceiver, royaltyFee);

        tokenMetadata[newTokenId] = NFTMetadata({
            nftType: nftType,
            creator: msg.sender,
            createdAt: block.timestamp,
            category: category
        });

        creatorTokens[msg.sender].push(newTokenId);

        emit NFTMinted(newTokenId, msg.sender, nftType, uri);

        return newTokenId;
    }

    /**
     * @dev Batch mint for collections (albums, series)
     */
    function batchMint(
        address to,
        string[] memory uris,
        NFTType nftType,
        string memory category,
        address royaltyReceiver,
        uint96 royaltyFee
    ) public returns (uint256[] memory) {
        uint256[] memory tokenIds = new uint256[](uris.length);

        for (uint256 i = 0; i < uris.length; i++) {
            tokenIds[i] = mint(to, uris[i], nftType, category, royaltyReceiver, royaltyFee);
        }

        return tokenIds;
    }

    /**
     * @dev Get all tokens created by an address
     */
    function getCreatorTokens(address creator) public view returns (uint256[] memory) {
        return creatorTokens[creator];
    }

    /**
     * @dev Get total supply
     */
    function totalSupply() public view returns (uint256) {
        return _tokenIds.current();
    }

    // Required overrides
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721URIStorage, ERC721Royalty)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function _burn(uint256 tokenId)
        internal
        override(ERC721, ERC721URIStorage, ERC721Royalty)
    {
        super._burn(tokenId);
    }
}
