import { Template } from 'aws-cdk-lib/assertions';
import * as cdk from 'aws-cdk-lib';
import { MyTraderPalStack } from '../lib/mytraderpal-stack';

test('MyTraderPal Stack', () => {
  const app = new cdk.App();
  const stack = new MyTraderPalStack(app, 'MyTraderPalTestStack');
  const template = Template.fromStack(stack);

  // Check if DynamoDB table exists
  template.hasResourceProperties('AWS::DynamoDB::Table', {
    TableName: 'mtp_app',
    BillingMode: 'PAY_PER_REQUEST',
  });

  // Check if Cognito User Pool exists
  template.hasResourceProperties('AWS::Cognito::UserPool', {
    UserPoolName: 'mytraderpal-users',
  });

  // Check if Lambda function exists
  template.hasResourceProperties('AWS::Lambda::Function', {
    Runtime: 'python3.12',
  });

  // Check if API Gateway exists
  template.hasResourceProperties('AWS::ApiGatewayV2::Api', {
    Name: 'mytraderpal-api',
  });
});
