# Enterprise AI Agent System

This directory contains the skills for the enterprise AI agent system.

## Skill Structure

```
skills/
├── public/           # Public skills (shared across all users)
│   ├── bootstrap/   # Bootstrap/onboarding skill
│   ├── research/    # Research and analysis skills
│   └── coding/      # Coding assistance skills
└── custom/          # Custom skills (user-specific)
    ├── company-a/   # Skills for Company A
    └── company-b/   # Skills for Company B
```

## Skill Development

To create a new skill:

1. Create a new directory in `custom/` with your skill name
2. Create a `SKILL.md` file with skill metadata
3. Add skill implementation files
4. Test the skill with the agent

## Public Skills

Public skills are available to all users and include:

- **Bootstrap**: Agent onboarding and personalization
- **Research**: Web research and information gathering
- **Coding**: Programming assistance and code review

## Custom Skills

Custom skills are organization or user-specific and can include:

- **Domain-specific knowledge**: Industry-specific expertise
- **Internal tools**: Integration with company systems
- **Custom workflows**: Business process automation