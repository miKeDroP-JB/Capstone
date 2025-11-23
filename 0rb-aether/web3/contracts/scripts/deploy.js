const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying 0RB_AETHER Contracts...\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);
  console.log("Account balance:", (await hre.ethers.provider.getBalance(deployer.address)).toString(), "\n");

  // Deploy NFT Contract
  console.log("📦 Deploying OrbNFT...");
  const OrbNFT = await hre.ethers.getContractFactory("OrbNFT");
  const orbNFT = await OrbNFT.deploy();
  await orbNFT.waitForDeployment();
  const nftAddress = await orbNFT.getAddress();
  console.log("✅ OrbNFT deployed to:", nftAddress);

  // Deploy Payments Contract
  console.log("\n📦 Deploying OrbPayments...");
  const OrbPayments = await hre.ethers.getContractFactory("OrbPayments");
  const orbPayments = await OrbPayments.deploy();
  await orbPayments.waitForDeployment();
  const paymentsAddress = await orbPayments.getAddress();
  console.log("✅ OrbPayments deployed to:", paymentsAddress);

  // Deploy Gaming Contract
  console.log("\n📦 Deploying OrbGaming...");
  const OrbGaming = await hre.ethers.getContractFactory("OrbGaming");
  const orbGaming = await OrbGaming.deploy();
  await orbGaming.waitForDeployment();
  const gamingAddress = await orbGaming.getAddress();
  console.log("✅ OrbGaming deployed to:", gamingAddress);

  // Fund gaming contract with house bankroll
  console.log("\n💰 Funding OrbGaming with initial bankroll...");
  const fundTx = await deployer.sendTransaction({
    to: gamingAddress,
    value: hre.ethers.parseEther("1.0")
  });
  await fundTx.wait();
  console.log("✅ Funded with 1 ETH");

  // Deploy Creator Token Factory
  console.log("\n📦 Deploying Creator Token (example)...");
  const OrbCreatorToken = await hre.ethers.getContractFactory("OrbCreatorToken");
  const creatorToken = await OrbCreatorToken.deploy(
    "0RB Creator Token",
    "0RBCT",
    deployer.address,
    hre.ethers.parseEther("1000") // Initial supply to creator
  );
  await creatorToken.waitForDeployment();
  const creatorTokenAddress = await creatorToken.getAddress();
  console.log("✅ OrbCreatorToken deployed to:", creatorTokenAddress);

  // Summary
  console.log("\n" + "=".repeat(60));
  console.log("🎉 DEPLOYMENT COMPLETE!");
  console.log("=".repeat(60));
  console.log("\nContract Addresses:");
  console.log("  OrbNFT:          ", nftAddress);
  console.log("  OrbPayments:     ", paymentsAddress);
  console.log("  OrbGaming:       ", gamingAddress);
  console.log("  OrbCreatorToken: ", creatorTokenAddress);
  console.log("\nNetwork:", hre.network.name);
  console.log("Chain ID:", (await hre.ethers.provider.getNetwork()).chainId.toString());

  // Save deployment info
  const fs = require("fs");
  const deploymentInfo = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    deployer: deployer.address,
    contracts: {
      OrbNFT: nftAddress,
      OrbPayments: paymentsAddress,
      OrbGaming: gamingAddress,
      OrbCreatorToken: creatorTokenAddress,
    },
    timestamp: new Date().toISOString(),
  };

  fs.writeFileSync(
    `deployments-${hre.network.name}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\n💾 Deployment info saved to deployments-" + hre.network.name + ".json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
