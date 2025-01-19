# AWS Hooks

The **AWS Hooks** application has two nodes to Export and Import annotation directly from AWS bucket.


## Quick Start:

1. Go to `Pipelines` and `Create new pipeline`.
2. Build a custom work flow that requires Export/Import annotations to/from AWS bucket
3. Define the bucket name and the region name in the node configuration panel.
4. Start pipeline

Pre-requirements: The AWS-hooks service needs an integration of `AWS_INTEGRATION` that holds the service account json data.  

Also, secret with the following  format can be used as well (put the secrete name in the integration name filed)

```
{
    "key": "your_access_key", 
    "secret": "your_secret_key"
}
```


## Node inputs and Outputs:

Both aws-hooks 2 nodes get the same item as input and output


## How it works:

### Export Annotations to AWS
When an item passes through the node, the node will export the item annotations to a json file and upload it to the AWS bucket. \
The file will be uploaded to the following location: \
`<driver_path>/<item.dir>/<item.name>.json`

### Import Annotations from AWS
When an item passes through the node, the node will download the item JSON annotations file from the AWS bucket and update the item with the new annotations. \
The file will be downloaded from the following location: \
`<driver_path>/<item.dir>/<item.name>.json`


## Node Configuration:

<img src="assets/node_configration.png" height="480">

**Configuration**

- **Node Name:** The display name on the canvas.
- **Bucket Name:** The bucket name to export/import the annotations
- **Region Name:** The region name of the bucket


## Contributions, Bugs and Issues - How to Contribute

We welcome anyone to help us improve this app.  
[Here's](CONTRIBUTING.md) a detailed instructions to help you open a bug or ask for a feature request.