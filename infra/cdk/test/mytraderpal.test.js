"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const assertions_1 = require("aws-cdk-lib/assertions");
const cdk = require("aws-cdk-lib");
const mytraderpal_stack_1 = require("../lib/mytraderpal-stack");
test('MyTraderPal Stack', () => {
    const app = new cdk.App();
    const stack = new mytraderpal_stack_1.MyTraderPalStack(app, 'MyTraderPalTestStack');
    const template = assertions_1.Template.fromStack(stack);
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoibXl0cmFkZXJwYWwudGVzdC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbIm15dHJhZGVycGFsLnRlc3QudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7QUFBQSx1REFBa0Q7QUFDbEQsbUNBQW1DO0FBQ25DLGdFQUE0RDtBQUU1RCxJQUFJLENBQUMsbUJBQW1CLEVBQUUsR0FBRyxFQUFFO0lBQzdCLE1BQU0sR0FBRyxHQUFHLElBQUksR0FBRyxDQUFDLEdBQUcsRUFBRSxDQUFDO0lBQzFCLE1BQU0sS0FBSyxHQUFHLElBQUksb0NBQWdCLENBQUMsR0FBRyxFQUFFLHNCQUFzQixDQUFDLENBQUM7SUFDaEUsTUFBTSxRQUFRLEdBQUcscUJBQVEsQ0FBQyxTQUFTLENBQUMsS0FBSyxDQUFDLENBQUM7SUFFM0MsaUNBQWlDO0lBQ2pDLFFBQVEsQ0FBQyxxQkFBcUIsQ0FBQyxzQkFBc0IsRUFBRTtRQUNyRCxTQUFTLEVBQUUsU0FBUztRQUNwQixXQUFXLEVBQUUsaUJBQWlCO0tBQy9CLENBQUMsQ0FBQztJQUVILG9DQUFvQztJQUNwQyxRQUFRLENBQUMscUJBQXFCLENBQUMsd0JBQXdCLEVBQUU7UUFDdkQsWUFBWSxFQUFFLG1CQUFtQjtLQUNsQyxDQUFDLENBQUM7SUFFSCxrQ0FBa0M7SUFDbEMsUUFBUSxDQUFDLHFCQUFxQixDQUFDLHVCQUF1QixFQUFFO1FBQ3RELE9BQU8sRUFBRSxZQUFZO0tBQ3RCLENBQUMsQ0FBQztJQUVILDhCQUE4QjtJQUM5QixRQUFRLENBQUMscUJBQXFCLENBQUMsd0JBQXdCLEVBQUU7UUFDdkQsSUFBSSxFQUFFLGlCQUFpQjtLQUN4QixDQUFDLENBQUM7QUFDTCxDQUFDLENBQUMsQ0FBQyIsInNvdXJjZXNDb250ZW50IjpbImltcG9ydCB7IFRlbXBsYXRlIH0gZnJvbSAnYXdzLWNkay1saWIvYXNzZXJ0aW9ucyc7XG5pbXBvcnQgKiBhcyBjZGsgZnJvbSAnYXdzLWNkay1saWInO1xuaW1wb3J0IHsgTXlUcmFkZXJQYWxTdGFjayB9IGZyb20gJy4uL2xpYi9teXRyYWRlcnBhbC1zdGFjayc7XG5cbnRlc3QoJ015VHJhZGVyUGFsIFN0YWNrJywgKCkgPT4ge1xuICBjb25zdCBhcHAgPSBuZXcgY2RrLkFwcCgpO1xuICBjb25zdCBzdGFjayA9IG5ldyBNeVRyYWRlclBhbFN0YWNrKGFwcCwgJ015VHJhZGVyUGFsVGVzdFN0YWNrJyk7XG4gIGNvbnN0IHRlbXBsYXRlID0gVGVtcGxhdGUuZnJvbVN0YWNrKHN0YWNrKTtcblxuICAvLyBDaGVjayBpZiBEeW5hbW9EQiB0YWJsZSBleGlzdHNcbiAgdGVtcGxhdGUuaGFzUmVzb3VyY2VQcm9wZXJ0aWVzKCdBV1M6OkR5bmFtb0RCOjpUYWJsZScsIHtcbiAgICBUYWJsZU5hbWU6ICdtdHBfYXBwJyxcbiAgICBCaWxsaW5nTW9kZTogJ1BBWV9QRVJfUkVRVUVTVCcsXG4gIH0pO1xuXG4gIC8vIENoZWNrIGlmIENvZ25pdG8gVXNlciBQb29sIGV4aXN0c1xuICB0ZW1wbGF0ZS5oYXNSZXNvdXJjZVByb3BlcnRpZXMoJ0FXUzo6Q29nbml0bzo6VXNlclBvb2wnLCB7XG4gICAgVXNlclBvb2xOYW1lOiAnbXl0cmFkZXJwYWwtdXNlcnMnLFxuICB9KTtcblxuICAvLyBDaGVjayBpZiBMYW1iZGEgZnVuY3Rpb24gZXhpc3RzXG4gIHRlbXBsYXRlLmhhc1Jlc291cmNlUHJvcGVydGllcygnQVdTOjpMYW1iZGE6OkZ1bmN0aW9uJywge1xuICAgIFJ1bnRpbWU6ICdweXRob24zLjEyJyxcbiAgfSk7XG5cbiAgLy8gQ2hlY2sgaWYgQVBJIEdhdGV3YXkgZXhpc3RzXG4gIHRlbXBsYXRlLmhhc1Jlc291cmNlUHJvcGVydGllcygnQVdTOjpBcGlHYXRld2F5VjI6OkFwaScsIHtcbiAgICBOYW1lOiAnbXl0cmFkZXJwYWwtYXBpJyxcbiAgfSk7XG59KTtcbiJdfQ==