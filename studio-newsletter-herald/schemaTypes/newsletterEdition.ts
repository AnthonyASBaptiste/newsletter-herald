import {defineType, defineField, defineArrayMember} from 'sanity'

export const newsletterEdition = defineType({
  name: 'newsletterEdition',
  title: 'Newsletter Edition',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      description: 'Headline or liturgical title for this newsletter edition',
      type: 'string',
      validation: (Rule) => Rule.required().error('Title is required'),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      description: 'URL-friendly identifier derived from target Sunday or edition title',
      type: 'slug',
      options: {
        source: (doc: Record<string, unknown>) =>
          (doc.targetSunday as string) || (doc.title as string) || '',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required().error('Slug is required'),
    }),
    defineField({
      name: 'sourceDocumentUrl',
      title: 'Source Document URL',
      description: 'Direct link to the original PDF or cloud storage document',
      type: 'url',
      validation: (Rule) =>
        Rule.uri({
          scheme: ['http', 'https'],
        }),
    }),
    defineField({
      name: 'sourceFilename',
      title: 'Source Filename',
      description: 'Original filename of the uploaded bulletin or newsletter PDF',
      type: 'string',
    }),
    defineField({
      name: 'publicationDate',
      title: 'Publication Date',
      description: 'Date the newsletter was originally published or issued',
      type: 'date',
      validation: (Rule) => Rule.required().error('Publication date is required'),
    }),
    defineField({
      name: 'targetSunday',
      title: 'Target Sunday',
      description: 'The upcoming Sunday liturgical date this newsletter addresses',
      type: 'date',
      validation: (Rule) => Rule.required().error('Target Sunday is required'),
    }),
    defineField({
      name: 'liturgicalOccasion',
      title: 'Liturgical Occasion',
      description: 'Specific liturgical feast or celebration (e.g. 26th Sunday in Ordinary Time)',
      type: 'string',
    }),
    defineField({
      name: 'liturgicalSeason',
      title: 'Liturgical Season',
      description: 'Church season (e.g. Ordinary Time, Advent, Christmas, Lent, Easter)',
      type: 'string',
    }),
    defineField({
      name: 'liturgicalYear',
      title: 'Liturgical Year',
      description: 'Liturgical reading cycle (e.g. Year A, Year B, Year C)',
      type: 'string',
    }),
    defineField({
      name: 'primaryTheme',
      title: 'Primary Theme',
      description: 'Core editorial theme linked to the Theme taxonomy',
      type: 'reference',
      to: [{type: 'theme'}],
      validation: (Rule) => Rule.required().error('Primary theme reference is required'),
    }),
    defineField({
      name: 'supportingThemes',
      title: 'Supporting Themes',
      description: 'Curated secondary themes linked from the Theme taxonomy',
      type: 'array',
      of: [
        defineArrayMember({
          type: 'reference',
          to: [{type: 'theme'}],
        }),
      ],
    }),
    defineField({
      name: 'summary',
      title: 'Summary',
      description: 'Structured two-paragraph editorial digest synthesized for parishioners',
      type: 'text',
      rows: 6,
      validation: (Rule) => Rule.required().error('Summary is required'),
    }),
    defineField({
      name: 'status',
      title: 'Status',
      description: 'Current editorial publication lifecycle status',
      type: 'string',
      options: {
        list: [
          {title: 'Draft', value: 'draft'},
          {title: 'Awaiting Review', value: 'awaiting_review'},
          {title: 'Approved', value: 'approved'},
          {title: 'Scheduled', value: 'scheduled'},
          {title: 'Sent', value: 'sent'},
          {title: 'Rejected', value: 'rejected'},
          {title: 'Failed', value: 'failed'},
        ],
      },
      initialValue: 'draft',
      validation: (Rule) =>
        Rule.required()
          .error('Status is required')
          .custom((val) => {
            const allowed = [
              'draft',
              'awaiting_review',
              'approved',
              'scheduled',
              'sent',
              'rejected',
              'failed',
            ]
            return (
              (val && allowed.includes(val as string)) ||
              `Status must be one of: ${allowed.join(', ')}`
            )
          }),
    }),
    defineField({
      name: 'validation',
      title: 'Editorial Validation',
      description: 'Pre-flight checks and confidence metrics assessed by the editorial agent',
      type: 'object',
      fields: [
        defineField({
          name: 'dateValid',
          title: 'Date Validated',
          description: 'Whether the target Sunday aligns with publication date and liturgical calendar',
          type: 'boolean',
        }),
        defineField({
          name: 'confidence',
          title: 'Confidence Score',
          description: 'Overall agent confidence in extraction and thematic alignment (0 to 1.0)',
          type: 'number',
          validation: (Rule) => Rule.min(0).max(1),
        }),
        defineField({
          name: 'checks',
          title: 'Validation Checklist',
          description: 'Specific assertions passed or evaluated by the agent',
          type: 'array',
          of: [
            defineArrayMember({
              type: 'string',
            }),
          ],
        }),
      ],
    }),
    defineField({
      name: 'aiGenerated',
      title: 'AI Generated',
      description: 'Indicates whether the initial draft and themes were prepared by an AI agent',
      type: 'boolean',
      initialValue: true,
      validation: (Rule) => Rule.required().error('AI Generated flag is required'),
    }),
    defineField({
      name: 'aiModel',
      title: 'AI Model',
      description: 'Model identifier used by the editorial agent (e.g. mistral-large, claude-3-5-sonnet)',
      type: 'string',
    }),
    defineField({
      name: 'createdAt',
      title: 'Created At',
      description: 'Timestamp when this edition was initially created',
      type: 'datetime',
      initialValue: () => new Date().toISOString(),
      validation: (Rule) => Rule.required().error('Creation timestamp is required'),
    }),
    defineField({
      name: 'updatedAt',
      title: 'Updated At',
      description: 'Timestamp when this edition was last modified',
      type: 'datetime',
      initialValue: () => new Date().toISOString(),
      validation: (Rule) => Rule.required().error('Update timestamp is required'),
    }),
  ],
  preview: {
    select: {
      title: 'title',
      targetSunday: 'targetSunday',
      status: 'status',
      liturgicalOccasion: 'liturgicalOccasion',
    },
    prepare({title, targetSunday, status, liturgicalOccasion}) {
      const statusLabel = status ? `[${status.replace(/_/g, ' ').toUpperCase()}]` : ''
      const subtitle = [
        liturgicalOccasion,
        targetSunday ? `Sunday: ${targetSunday}` : '',
        statusLabel,
      ]
        .filter(Boolean)
        .join(' • ')
      return {
        title: title || 'Untitled Newsletter Edition',
        subtitle,
      }
    },
  },
})
