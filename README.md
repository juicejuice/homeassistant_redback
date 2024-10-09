# Redback Technologies integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Redback Technologies (https://redbacktech.com/) produces a range of inverter and battery systems. This integration uses the Redback Technologies Portal (public API) to sync solar and battery energy data with Home Assistant.

## Pre-requisites

You need to contact Redback Technologies support team to request API access. This appears to be available to any customer who asks. You will receive access details including "Client ID" and "Credential" which are necessary for this integration.

## Installation

Install the repository through HACS (it should appear in the list of available integrations) or by manually copying the `custom_components/redback` folder into your `custom_components` folder.

## Configuration

Once you have installed the component, it should be available for configuration through the user interface.

To setup the integration, go to Configuration -> Integrations, and search for Redback Technologies Portal.

Use the client ID and credential (secret) supplied by Redback support team. Client ID goes in "Redback ID" field and Credential goes in "Redback Authentication" field. You can also give the device a friendly name to suit your needs.

The "Redback Site" field is only required when you have multiple Redback inverters. If you have a single inverter then leave this field alone. For multiple inverters, each inverter is a "site", and you simply indicate which inverter you are setting up (first, second, third, etc.). In other words, add the Redback device integration multiple times and change this field each time to select another inverter. BTW, you can see the full list of sites/inverters by using the Redback API yourself, this integration doesn't enumerate the list for you (although pull requests are always welcome :]).

No further configuration is required. Errors will be reported in the log.

Re-authentication of Redback devices is supported; Home Assistant will notify you when the previously working Redback API credentials expire. In this case, you can choose to re-configure from the integrations page and enter your new Redback API credentials. It is not possible to manually trigger re-authentication, but you can update credentials by hand by editing the `core.config_entries` file in the Home Assistant `.storage` folder (search for "redback" to find the configuration items).

## Usage

The Redback Technologies data source is updated every minute by your inverter. This integration will automatically read the data every minute and update the relevant HA entities, e.g., "Grid Import Total".

## Notes

- This was developed for the ST10000 Smart Hybrid (three phase) inverter with integrated battery
- This has been tested for the SH5000 Smart Hybrid (single phase) inverter with integrated battery (thanks to "pcal" from HA Community forums)
- This has also been tested for other inverters now, including those without battery (thanks djgoding and LachyGoshi)
- Please file any issues at the Github site
- I have provided sufficient sensor entities to drive the "Energy" dashboard on HA, you just need to configure your dashboard with the relevant "Total" sensors

## Private API (DEPRECATED)

**NOTE: the private API method is now deprecated and no longer available for use. I've left the notes below for reference, in case this API method becomes useful again in future.**

I first developed this integration using what I call the "private API". This is the RESTful API used by the vendor's portal and mobile app to obtain the solar and battery data for your system. You can try the private API if you like, but I guess Redback can change this upon a whim, whereas the public API is (presumably) properly maintained for downstream consumers.

To try out the private API you will need to enter your serial number in the "Redback ID" field and application cookie in the "Redback Authentication" field. The value for that field should be in the form .AspNet.ApplicationCookie=XXX, where XXX is the big long cookie value obtained from Chrome Developer Tools, Application tab, after logging in to the [vendor portal](https://portal.redbacktech.com/).

Please also note, I haven't re-tested the private API since developing the public API method. Something may be broken or missing. Also, the private API auth token will probably expire and you would need to manually refresh it in the integration's config files (I haven't added a UI for refreshing private API token).
