import {defineType, defineField, defineArrayMember} from 'sanity'

export const editorialWorkflow = defineType({
  name: 'editorialWorkflow',
  title: 'Editorial Workflow',
  type: 'document',
  fields: [
    defineField({
      name: 'newsletter',
      title: 'Newsletter Edition',
      description: 'The newsletter edition governed by this workflow',
      type: 'reference',
      to: [{type: 'newsletterEdition'}],
      validation: (Rule) => Rule.required().error('Newsletter edition reference is required'),
    }),
    defineField({
      name: 'currentStage',
      title: 'Current Stage',
      description: 'Current stage in the editorial governance pipeline',
      type: 'string',
      options: {
        list: [
          {title: 'Received', value: 'received'},
          {title: 'Processing', value: 'processing'},
          {title: 'Draft', value: 'draft'},
          {title: 'Awaiting Review', value: 'awaiting_review'},
          {title: 'Approved', value: 'approved'},
          {title: 'Scheduled', value: 'scheduled'},
          {title: 'Sent', value: 'sent'},
        ],
      },
      initialValue: 'received',
      validation: (Rule) =>
        Rule.required()
          .error('Current stage is required')
          .custom((val) => {
            const allowed = [
              'received',
              'processing',
              'draft',
              'awaiting_review',
              'approved',
              'scheduled',
              'sent',
            ]
            return (
              (val && allowed.includes(val as string)) ||
              `Current stage must be one of: ${allowed.join(', ')}`
            )
          }),
    }),
    defineField({
      name: 'assignedAgent',
      title: 'Assigned Agent',
      description: 'Identifier of the AI editorial agent handling automated tasks',
      type: 'string',
    }),
    defineField({
      name: 'reviewer',
      title: 'Human Reviewer',
      description: 'Name or email of the human editor reviewing the edition',
      type: 'string',
    }),
    defineField({
      name: 'decision',
      title: 'Review Decision',
      description: 'Human editorial gate decision',
      type: 'string',
      options: {
        list: [
          {title: 'Pending', value: 'pending'},
          {title: 'Approved', value: 'approved'},
          {title: 'Rejected', value: 'rejected'},
        ],
      },
      initialValue: 'pending',
      validation: (Rule) =>
        Rule.custom((val) => {
          if (!val) return true
          const allowed = ['pending', 'approved', 'rejected']
          return allowed.includes(val as string) || `Decision must be one of: ${allowed.join(', ')}`
        }),
    }),
    defineField({
      name: 'decisionAt',
      title: 'Decision Timestamp',
      description: 'Timestamp when the human review decision was executed',
      type: 'datetime',
    }),
    defineField({
      name: 'history',
      title: 'Workflow History',
      description: 'Immutable chronological audit trail of editorial stages and actions',
      type: 'array',
      of: [
        defineArrayMember({
          type: 'object',
          name: 'workflowHistoryEntry',
          title: 'Workflow History Entry',
          fields: [
            defineField({
              name: 'stage',
              title: 'Stage',
              type: 'string',
              validation: (Rule) => Rule.required().error('History stage is required'),
            }),
            defineField({
              name: 'actor',
              title: 'Actor',
              description: 'Agent or user responsible for this state transition',
              type: 'string',
              validation: (Rule) => Rule.required().error('History actor is required'),
            }),
            defineField({
              name: 'note',
              title: 'Note',
              description: 'Optional commentary or reason for state transition',
              type: 'text',
              rows: 2,
            }),
            defineField({
              name: 'timestamp',
              title: 'Timestamp',
              type: 'datetime',
              initialValue: () => new Date().toISOString(),
              validation: (Rule) => Rule.required().error('History timestamp is required'),
            }),
          ],
          preview: {
            select: {
              stage: 'stage',
              actor: 'actor',
              timestamp: 'timestamp',
            },
            prepare({stage, actor, timestamp}) {
              const formattedDate = timestamp ? new Date(timestamp).toLocaleString() : ''
              return {
                title: `${stage || 'Unknown stage'} • ${actor || 'Unknown actor'}`,
                subtitle: formattedDate,
              }
            },
          },
        }),
      ],
    }),
  ],
  preview: {
    select: {
      newsletterTitle: 'newsletter.title',
      stage: 'currentStage',
      decision: 'decision',
    },
    prepare({newsletterTitle, stage, decision}) {
      return {
        title: newsletterTitle ? `Workflow: ${newsletterTitle}` : 'Editorial Workflow',
        subtitle: `Stage: ${stage || 'N/A'} • Decision: ${decision || 'pending'}`,
      }
    },
  },
})
