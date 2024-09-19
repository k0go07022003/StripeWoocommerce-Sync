# StripeWoo Sync

StripeWoo Sync is an integration tool that seamlessly connects Stripe payments with WooCommerce orders, providing automatic synchronization and easy management through a user-friendly admin panel.

## About StripeWoo Sync

StripeWoo Sync was created to bridge the gap between Stripe's powerful payment processing capabilities and WooCommerce's robust e-commerce platform. This tool allows businesses to leverage the strengths of both systems while maintaining a unified order management process.

...

## About the Creator

StripeWoo Sync was created by Szymek Automatyk.

## Community

Join our Discord community for StripeWoo Sync support, to share ideas, or just to chat about the project:

[![Discord](https://img.shields.io/discord/YOUR_DISCORD_SERVER_ID?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/NCMYbbnJve)

[Join our Discord server](https://discord.gg/NCMYbbnJve)

## Installation

You have two options for installation:

### Option 1: Using the install script (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/k0go07022003/StripeWoocommerce-Sync.git
   cd StripeWoocommerce-Sync
   ```

2. Run the installation script:
   ```
   python install.py
   ```

   This script will:
   - Install all required dependencies
   - Create the database
   - Guide you through creating an admin account

3. After the installation is complete, you can run the application:
   ```
   python run.py
   ```

### Option 2: Manual installation

1. Clone the repository:
   ```
   git clone https://github.com/k0go07022003/StripeWoocommerce-Sync.git
   cd StripeWoocommerce-Sync
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the configuration:
   - Edit `src/config/config.yaml` and fill in your database settings

5. Create the database and admin user:
   ```
   python -m src.create_admin
   ```

6. Run the application:
   ```
   python run.py
   ```

The application should now be running at `http://localhost:5000`.

## Configuration

After installation, log in to the admin panel at `http://localhost:5000/admin` and navigate to the Settings page to configure your WooCommerce and Stripe credentials.

## Usage

1. Create product mappings in the admin panel
2. Set up a Stripe webhook to point to `http://your-domain.com/webhook`
3. When a payment is made through Stripe, the application will automatically create a corresponding order in WooCommerce

## Development

To run the application in debug mode:
```
python run.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any problems or have any questions, please open an issue on GitHub.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Stripe](https://stripe.com/)
- [WooCommerce](https://woocommerce.com/)
- [Tailwind CSS](https://tailwindcss.com/)
