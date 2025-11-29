# Software Development Life Cycle (SDLC) Model

## Chosen Model: Agile/Scrum

### Justification

For the MyTraderPal trading journal application, I chose the **Agile/Scrum** SDLC model for the following reasons:

#### 1. **Iterative Development**
- The application started as a minimal viable product (MVP) with core features (notes and strategies)
- Agile allows for incremental development, adding features in sprints
- This aligns with the assignment requirements of building a minimal app first, then improving it

#### 2. **Flexibility and Adaptability**
- Requirements can evolve as we learn more about user needs
- Easy to pivot or adjust features based on feedback
- Perfect for a student project where requirements may change

#### 3. **Rapid Feedback Loops**
- Short development cycles (sprints) allow for quick validation
- Continuous integration and testing provide immediate feedback
- Aligns with DevOps practices (CI/CD pipeline)

#### 4. **Small Team Size**
- Agile/Scrum works well for individual or small team projects
- No need for extensive documentation overhead
- Focus on working software over comprehensive documentation

#### 5. **DevOps Integration**
- Agile practices complement DevOps automation
- CI/CD pipelines support continuous delivery
- Automated testing fits naturally into sprint cycles

### SDLC Phases in This Project

#### Phase 1: Planning & Requirements (Assignment 1)
- Defined core features: Notes CRUD, Strategies CRUD
- Chose technology stack: Python Lambda, DynamoDB, Next.js
- Created architecture diagram

#### Phase 2: Design
- Designed single-table DynamoDB schema
- Planned API endpoints
- Created frontend component structure

#### Phase 3: Implementation (Assignment 1)
- Built backend API with Lambda
- Created frontend with Next.js
- Implemented authentication with Cognito

#### Phase 4: Testing
- Added unit tests (84% coverage)
- Integration tests for API endpoints
- Offline testing with mocks

#### Phase 5: Deployment
- Infrastructure as Code with AWS CDK
- Automated deployment pipeline
- Containerization with Docker

#### Phase 6: Monitoring & Improvement (Assignment 2)
- Added health checks and metrics
- Implemented Prometheus monitoring
- Refactored code following SOLID principles

### Why Not Waterfall?

- **Too rigid**: Waterfall requires complete requirements upfront
- **No iteration**: Difficult to adapt to changing needs
- **Late testing**: Testing happens only at the end
- **Not suitable for DevOps**: Doesn't support continuous delivery

### Why Not DevOps Alone?

- DevOps is a **culture and practice**, not an SDLC model
- DevOps complements Agile by automating the delivery pipeline
- We use Agile for development process, DevOps for automation

### Conclusion

Agile/Scrum is the ideal choice for this project because it:
- Supports iterative development from minimal to full-featured app
- Enables rapid adaptation to requirements
- Integrates seamlessly with DevOps practices
- Works well for individual/small team projects
- Focuses on working software and continuous improvement

