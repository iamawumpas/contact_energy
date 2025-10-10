<table>
  <tr>
    <td style="vertical-align: top;">
  <img src="/logo.svg" alt="Contact Energy Logo" width="auto" height="50px" style="vertical-align: top; display: inline-block;">
    </td>
    <td >
      <h1>Contact Energy</h1>
      <h4>Let's do the energy thing</h4>
    </td>
  </tr>
  <tr>
    <td colspan="2" style="border: none; vertical-align: top;">
  <strong>version:</strong> 0.4.2
    </td>
  </tr>
</table>

My implementation of the **Home Assistant** Contact Energy integration in HACS, to fix bugs on my HA instance.

## Why make my own version
I have used ***cody1515's*** original integration, and later, ***notf0und's*** fork, to access my energy usage from Contact Energy (a New Zealand electricity supplier) for several years now.

However, for some reason since August 2025, the integration has refused to download my usage data, while all other Contact Energy data was being updated. I assumed it was a change to Contact Energy's api structure, but then again their app hasn't been updated recently and it works fine. So I decided to see if the integration could be fixed.

The logs showed the integration failing for a number of reasons:
- timing out
- not initiallising
- errors calling the ICP number for the account
- authentication issues

So time for some digging and hopefully patching.

<code style="color : orange;">**THIS IS NOT A FORK**</code> - but a modifcation for my own use. In time I might discuss forking this project if I can get more out of the integration.

## What does the integration do?

All it does is download the current energy usage and billing information from your Contact Energy account in the same way that the smartphone app gathers your data for you to view.

The integration creates two groups of entities:

- The first group are the ***energy usage*** and ***free energy useage*** (if you take advantage of the free energy option). This data is stored in the Home Assistant statistics database and is visualised in the energy dashboard.
- The second group contain the sensors that expose the following information to dashboard cards
  - Due date for current bill
  - current bill amount
  - next reading date (although this has not always been reliable in my use-case)
  - next bill amount
  - next bill due date
  - and some other stuff I can't remember off hand (note: to self to update this someday).


## Limitations

The data provided by Contact Energy is significantly limited, and so there are caveats to the usefulness of this integration.

- **the most important** There is no real-time monitoring
Contact Energy makes your energy usage available to download, anywhere between 24-72 hours after the day of use. So, you will only every be looking at your **historical usage**. You will be able to see monthly, daily and hourly statistics once the data has been downloaded. <br><br>**Some context:** The Genesis smartmeters installed in most NZ homes since the 1990s report back to their host using the cellular network once a day (<https://www.ea.govt.nz/your-power/meters/>)

- **the integration can crash from time-to-time.** It has been observed by myself and [one other person](https://github.com/notf0und/ha-contact-energy/issues/1), that the integration stops downloading data from the Contact energy server. The solution is:  

1. Restart Home Assistant (OK solution)  
2. create a script to restart the integration as a cron job or internally using HA. I have done this, although I don't have a copy of the script/YAML on hand (stoopidly forgot to save a copy of it).

# Free to use

If anyone finds this repository, you are free to use the code as is - no warranties are provided. It works for me. I may, in the future modify the functionality to get more information for my HA instance.


# **Installation**  

## **HACS (Recommended)**  

1. Ensure [HACS is installed](https://hacs.xyz/docs/setup/download).  
2. Click the button below to open the repository in HACS:  
   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=iamawumpas&repository=contact_energy&category=integration)  
3. Install the **Contact Energy** integration.  
4. Restart Home Assistant.  

### **Manual Installation**  

1. Download the integration files from the repository.  
2. Copy all files from `custom_components/contact_energy` to your Home Assistant folder `config/custom_components/contact_energy`
4. Restart Home Assistant

## Getting started

1. Open Home Assistant and navigate to:
2. Settings → Devices & Services → + Add Integration
3. Search for Contact Energy and select it.
4. Enter the required details:

- Email & Password: Use the credentials for your Contact Energy account.
- Usage Days: Number of days to fetch data from Contact Energy's API (Recommended: 10 days).

Once configured, the integration will begin fetching and displaying your account and usage data.
A prompt will asking for email, password and usage days.

## Viewing Usage Data and Costs in Home Assistant

To see your electricity usage and costs in Home Assistant’s Energy Dashboard, follow these steps:

1. Go to → Settings → Dashboards → Energy
2. Click "Add Consumption" and select:

- Contact Energy - Electricity (xxx)
  - where **xxx** represents your ICP number
- Select one from  ***Select how Home Assistant should keep track of the costs of consumed energy.***
  - I usually select ***Do not track costs*** as I am more interested in kwh rather than the price
  - This is a feature from cody1515's original implementation and I have not tested it out fully. Have a play- let me know the results.

3. If you have other services on your account (for example Free Energy from 9pm-midnight, or Free energy weekends), click "Add Consumption" again and repeat Step 2.
- Contact Energy - Free Electricity (xxx) 
  - where **xxx** is your ICP number. Make sure you select the same ICP number as before if you are monitoring more than one dwelling.


# Attribution and Acknowledgments

- original project by [codyc1515](https://github.com/codyc1515/ha-contact-energy).
- fork by [notfound](https://github.com/notf0und/ha-contact-energy).
