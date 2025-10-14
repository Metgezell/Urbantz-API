# Code Review Guidelines

## Pre-Review Checklist
- Review the changes on [branch name]
- Ensure you understand the context and purpose of the changes

## Core Review Areas

### 1. Data Flow & Architecture
- Think through how data flows in the app
- Explain new patterns if they exist and why they were chosen
- Consider if the changes maintain or improve architectural consistency

### 2. Infrastructure Impact
- Were there any changes that could affect infrastructure?
- Consider deployment implications and resource requirements
- Check for any hardcoded values that should be configurable

### 3. User Experience States
- Consider empty, loading, error, and offline states
- Ensure graceful degradation when services are unavailable
- Verify user feedback is appropriate for all scenarios

### 4. Frontend Accessibility (a11y)
- Review frontend changes for accessibility compliance:
  - Keyboard navigation works properly
  - Focus management is correct
  - ARIA roles are used appropriately
  - Color contrast meets WCAG guidelines
  - Screen reader compatibility

### 5. API Compatibility
- If public APIs have changed, ensure backwards compatibility
- Consider incrementing API version if breaking changes are necessary
- Update API documentation if applicable

### 6. Dependencies
- Did we add any unnecessary dependencies?
- If there's a heavy dependency, could we inline a more minimal version?
- Check for security vulnerabilities in new dependencies
- Consider bundle size impact

### 7. Testing Quality
- Did we add quality tests?
- Prefer fewer, high-quality tests over many low-quality ones
- Prefer integration tests for user flows
- Ensure edge cases are covered

### 8. Database Schema
- Were there schema changes which could require a database migration?
- Consider data migration scripts if needed
- Verify foreign key relationships are properly maintained

### 9. Security Review
- Changes to auth flows or permissions? Run `/security-review`
- Check for potential security vulnerabilities
- Ensure sensitive data is properly protected
- Verify input validation and sanitization

### 10. Feature Flags
- If feature flags are set up, does this change require adding a new one?
- Consider gradual rollout strategies
- Ensure feature flags can be safely removed later

### 11. Internationalization (i18n)
- If i18n is set up, are the strings added localized?
- Are new routes internationalized?
- Consider right-to-left (RTL) language support if applicable

### 12. Performance & Caching
- Are there places we should use caching?
- Consider performance implications of the changes
- Check for potential memory leaks or performance bottlenecks

### 13. Observability & Logging
- Are we missing critical observability or logging on backend changes?
- Ensure proper error tracking and monitoring
- Consider adding metrics for new functionality
- Verify logs contain sufficient context for debugging

## Additional Considerations

### Code Quality
- Is the code readable and well-documented?
- Are naming conventions consistent?
- Is the code DRY (Don't Repeat Yourself)?
- Are there any code smells or anti-patterns?

### Performance
- Does the code perform efficiently?
- Are there any obvious performance bottlenecks?
- Consider scalability implications

### Maintainability
- Will this code be easy to maintain and extend?
- Are there clear separation of concerns?
- Is the code modular and reusable where appropriate?

## Review Process
1. Start with the big picture - understand the overall change
2. Review each file systematically
3. Test the changes if possible
4. Provide constructive feedback
5. Approve only when all concerns are addressed

## Approval Criteria
- All guidelines above have been considered
- No security vulnerabilities identified
- Code quality meets team standards
- Tests are adequate and passing
- Documentation is updated if needed
