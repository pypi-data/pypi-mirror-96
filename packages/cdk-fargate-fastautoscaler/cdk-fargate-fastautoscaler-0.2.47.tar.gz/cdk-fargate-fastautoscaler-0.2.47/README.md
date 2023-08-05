[![awscdk-jsii-template](https://img.shields.io/badge/built%20with-awscdk--jsii--template-blue)](https://github.com/pahud/awscdk-jsii-template)
[![NPM version](https://badge.fury.io/js/cdk-fargate-fastautoscaler.svg)](https://badge.fury.io/js/cdk-fargate-fastautoscaler)
[![PyPI version](https://badge.fury.io/py/cdk-fargate-fastautoscaler.svg)](https://badge.fury.io/py/cdk-fargate-fastautoscaler)
![Build](https://github.com/aws-samples/aws-fargate-fast-autoscaler/workflows/Build/badge.svg)

## aws-fargate-fast-autoscaler

**AWS Fargate Fast Autosaler** - A Serverless Implementation that Triggers your AWS Fargate autoscaling in seconds with `cdk-fargate-fastautoscaler`.

## cdk-fargate-fastautoscaler

`cdk-fargate-fastautoscaler` is a [aws/jsii](https://github.com/aws/jsii) construct library for AWS CDK.

By building your AWS CDK stacks with `cdk-fargate-fastautoscaler`, you can create your customized Fargate workload with the fast autoscaling capabilities.

![](images/fargate-fast-autoscaler.png)

# How it works

Behind the scene, our workload in PHP, NodeJS, Java or Python is running with a nginx reverse proxy within a single AWS Fargate Task exposing a `/nginx_status` endpoint for realtime connections info generation. All traffic coming through ALB to Fargate tasks will establish active connecitons with the nginx reverse proxy before it can hit our backend server.

We are running an AWS Step Function state machine to periodically invoke the AWS Lambda function and collect active connection numbers from each Fargate Task **every 3 seconds** and determine our scaling policy in the state machine followed by immediate `ecs service update` to increase the desired number of Fargate tasks.

# AWS CDK Sample

The following CDK sample creates a PHP service in AWS Fargate with the nginx as the reverse proxy.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
import aws_cdk.aws_ec2 as ec2
from aws_cdk.aws_ecs import AwsLogDriver, ContainerImage
from cdk_fargate_fastautoscaler import FargateFastAutoscaler
import path as path

app = cdk.App()

env = {
    "region": process.env.CDK_DEFAULT_REGION,
    "account": process.env.CDK_DEFAULT_ACCOUNT
}

stack = cdk.Stack(app, "FargateFastAutoscalerDemo", env=env)

vpc = ec2.Vpc.from_lookup(stack, "Vpc", is_default=True)

FargateFastAutoscaler(stack, "FargateFastAutoscaler",
    vpc=vpc,
    # create the backend PHP service
    backend_container={
        "image": ContainerImage.from_asset(path.join(__dirname, "../../sample/backend/php"))
    },
    # PHP service running on container port 2015
    backend_container_port_mapping=[{"container_port": 2015}]
)
```

On deployment complete, you'll see the URL in the Outputs:

**fargate-fast-autoscaling.URL** = http://farga-exter-1GW64WGQYNE4O-1567742142.us-west-2.elb.amazonaws.com

Open this URL and you will see the Caddy web server welcome page with phpinfo.

![](images/php-welcome.png)

And if you append `/nginx_status` in the URL and reload the page, you'll see this page:

![](images/nginx-status.png)

### Start your state machine

Go to Step Function console and click **start execution** on the state machines. Leave the execution name and input column as is and click **start execution** again. Your state machine will be running. Behind the scene the step function will invoke a Lambda function to collect **Active Connections** number from nginx reverse proxy on each fargate task and determine a new desired number of fargate tasks to scale. Typically it would just take **less than 10 seconds** before it starts to scale.

![](images/stepfunc.png)

# SNS Service Integration

The **SNSScaleOut** task in the state machine leverages direct Amazon SNS service integration to publish a notification to your SNS topic. You will receive SNS notification when it starts **ServiceScaleOut** task.

Specify the `snsTopic` property to define your custom SNS topic. If not defined, the construct will create a default SNS topic.

# Disable Scale In

By default, `disableScaleIn` is set to true to prevent your workload from scale-in. If you prefer to enable scale in, set `disableScaleIn` to `false`.

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
