# Nordic Python LTE CLI for Mesh Gateway Interfacing

This python program allows the user to interface with a connected nRF Cloud Connected Mesh Gateway.

## Requirements
- Python 3.0 or later
- Gateway must already be added and connected to nRF Cloud
- You must make an "account device" and acquire the following certificates via this nRF Cloud REST 
  endpoint: `POST https://api.nrfcloud.com/v1/account/certificates`
    - caCert.crt
    - clientCert.crt
    - privateKey.key
- You must have paho-mqtt installed for python3: `pip3 install paho-mqtt`

## Process
### Subnets
Subnets must be added to or generated on the gateway via the main menu option before subnets can be
added to nodes or before devices can be provisioned into subnets other than the primary subnet.

### Application Keys
Application keys must be added to or generated on the gateway via the main menu option before they 
can be binded to mesh models on nodes.

### Setting Up Nodes
In order to set up mesh network nodes, the following steps must be performed:

1. Add or generate a new subnet on the gateway if a subnet other than the primary subnet is desired.
2. Provision a new device into the mesh network using the desired subnet.
3. Add or generate a new applicaiton key on the gateway.
4. Bind the new application key to the desired model within the element of the desired node.
5. Set the publish parameters of the model within the element of the desired node. This includes
setting the publish address which this models messages with be sent on.
6. Add subscribe addresses as needed so that the desired model can recieve the appropriate model
messages being published by other models in the mesh network.

## Usage
1. Run the cli:

    `python3 cli.py`

2. Enter you nRF Cloud account API key and press enter when prompted.
3. Enter the number option associated with the mesh gateway device that you'd like to connect to.
4. From the main menu, enter the number option associated with the operation you'd like to perform.

### Main Menu
0. View unprovisioned device beacons - Get a list of live unprovisioned device beacons from the
gateway. A list of the unprovisioned device beacons will be printed to the screen.
1. Provision device - Provision a device and add it to the mesh network. You will be prompted to
enter provisioning details.
2. Configure network subnets - Add, Generate, Delete, or Get subnets for the gateway. You will be
prompted to enter subnet details.
3. Configure network applicaiton keys - Add, Genreate, Delete, or Get application keys for the
gateway. You will be prompted to enter application key details.
4. View network nodes - Get a list of network nodes. A list of network nodes will be printed to the
screen.
5. Discover a network node - Get all detailes from a node including:
    - IDs
    - Node settings
    - Mesh features
    - Element details
    - Model details
6. Configure a network node - Make configuration changes on a node including:
    0. Set Network Beacons - Enable or Disable the node's Network Beacon.
    1. Set Time-to-Live - Set the default Time-to-Live value for publishing messages.
    2. Set Relay Feature - Enable or Disable the Relay feature and set the retransmit count and
    interval for publishing relay messages.
    3. Set GATT PRoxy Feature - Enable or Disable the GATT Proxy feature of a node.
    4. Set Friend Feature - Enable or Disable the Friend feature of a node.
    5. Add Subnet - Add a Subnet to a node to allow it to participate in a new subnet.
    6. Delete Subnet - Delete a Subnet from a node to prevent it from participating ina subnet any
    longer.
    7. Bind Application Key - Bind an applicaiton key to a mesh model on a node.
    8. Unbind Application Key - Unbind an application key from a mesh model on a node.
    9. Set Publish Parameters - Set the publish parameters for a mesh model on a node.
    10. Add Subscribe Address - Add a subscribe address to a mesh model on a node so that it can
    recieve messages from other mesh models on the network.
    11. Delete Subscribe Address - Delete a subscribe address from a node so that it no longer
    recieved messages from other mesh models on the network.
    12. Overwrite Subscribe Address - Overwrite all existing subscribe address on a node with one
    new subscribe address.
7. Reset a network node - Un-provision a node so that it no longer participates in the mesh network
and starts broadcasting an unprovisioned device beacon.
