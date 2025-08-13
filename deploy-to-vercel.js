const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m'
};

console.log(`${colors.bright}${colors.blue}=== LED Display Website - Vercel Deployment Script ===${colors.reset}\n`);

// Check if Vercel CLI is installed
try {
  console.log(`${colors.yellow}Checking if Vercel CLI is installed...${colors.reset}`);
  execSync('vercel --version', { stdio: 'ignore' });
  console.log(`${colors.green}✓ Vercel CLI is installed${colors.reset}`);
} catch (error) {
  console.log(`${colors.red}✗ Vercel CLI is not installed${colors.reset}`);
  console.log(`${colors.yellow}Installing Vercel CLI...${colors.reset}`);
  try {
    execSync('npm install -g vercel', { stdio: 'inherit' });
    console.log(`${colors.green}✓ Vercel CLI installed successfully${colors.reset}`);
  } catch (installError) {
    console.error(`${colors.red}Failed to install Vercel CLI. Please install it manually with 'npm install -g vercel'${colors.reset}`);
    process.exit(1);
  }
}

// Ensure the admin-complete-supabase.html file exists
console.log(`${colors.yellow}Checking if admin-complete-supabase.html exists...${colors.reset}`);
if (!fs.existsSync('admin-complete-supabase.html')) {
  console.log(`${colors.yellow}admin-complete-supabase.html not found. Running combine script...${colors.reset}`);
  try {
    execSync('node combine_admin_files.js', { stdio: 'inherit' });
    console.log(`${colors.green}✓ Combined admin files successfully${colors.reset}`);
  } catch (error) {
    console.error(`${colors.red}Failed to combine admin files: ${error.message}${colors.reset}`);
    process.exit(1);
  }
}

// Validate vercel.json
console.log(`${colors.yellow}Validating vercel.json...${colors.reset}`);
try {
  const vercelConfig = JSON.parse(fs.readFileSync('vercel.json', 'utf8'));
  console.log(`${colors.green}✓ vercel.json is valid${colors.reset}`);
} catch (error) {
  console.error(`${colors.red}Invalid vercel.json: ${error.message}${colors.reset}`);
  console.log(`${colors.yellow}Please fix vercel.json before deploying${colors.reset}`);
  process.exit(1);
}

// Deploy to Vercel
console.log(`\n${colors.bright}${colors.blue}=== Deploying to Vercel ===${colors.reset}`);
console.log(`${colors.yellow}Choose deployment type:${colors.reset}`);
console.log(`1. Preview deployment (default)`);
console.log(`2. Production deployment`);

const readline = require('readline').createInterface({
  input: process.stdin,
  output: process.stdout
});

readline.question(`Enter your choice (1 or 2): `, (choice) => {
  readline.close();
  
  try {
    if (choice === '2') {
      console.log(`${colors.yellow}Deploying to production...${colors.reset}`);
      execSync('vercel --prod', { stdio: 'inherit' });
    } else {
      console.log(`${colors.yellow}Creating preview deployment...${colors.reset}`);
      execSync('vercel', { stdio: 'inherit' });
    }
    console.log(`${colors.green}${colors.bright}✓ Deployment completed successfully!${colors.reset}`);
    console.log(`\n${colors.yellow}To access your admin panel, go to your deployment URL + /admin-complete-supabase.html${colors.reset}`);
  } catch (error) {
    console.error(`${colors.red}Deployment failed: ${error.message}${colors.reset}`);
    process.exit(1);
  }
});