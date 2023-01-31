# Redback Technologies integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Redback Technologies (https://redbacktech.com/) produces a range of inverter and battery systems. This integration uses the Redback Technologies public API to sync solar and battery energy data with Home Assistant. An option for private API is supported, too.

## Installation

Install the repository through HACS by adding a custom repository or by manually copying the `custom_components/redback` folder into your `custom_components` folder.

## Configuration

The component is configured through the user interface.

To setup the integration, got to Configuration -> Integrations, and search for Redback Technologies.

Select "public" API method. Use the client ID and credential (secret) supplied by Redback support team. Client ID goes in "Redback ID" field and Credential goes in "Redback Authentication" field.

No further configuration is required. Errors will be reported in the log.

## Usage

The Redback Technologies data source is updated every minute by your inverter. This integration will automatically read the data every minute and update the relevant HA entities, e.g., "Grid Import Total".

## Notes

- This was developed for the ST10000 Smart Hybrid (three phase) inverter with integrated battery
- If you have a different model I would be interested to adapt the code to suit, but would need some data packets from your system
- I have provided sufficient sensor entities to drive the "Energy" dashboard on HA, you just need to configure your dashboard with the relevant "Total" sensors

## Private API

I first developed this integration using what I call the "private API". This is the RESTful API used by the vendor's portal and mobile app to obtain the solar and battery data for your system. You can try the private API if you like, but I guess Redback can change this upon a whim, whereas the public API is (presumably) properly maintained for downstream consumers.

To try out the private API you will need to enter your serial number in the "Redback ID" field and application cookie in the "Redback Authentication" field. The value for that field should be in the form .AspNet.ApplicationCookie=XXX, where XXX is the big long cookie value obtained from Chrome Developer Tools, Application tab, after logging in to the [vendor portal](https://portal.redbacktech.com/).

Please also note, I haven't re-tested the private API since developing the public API method. Something may be broken or missing.
