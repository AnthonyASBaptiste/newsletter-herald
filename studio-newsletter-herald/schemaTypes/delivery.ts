import {defineType, defineField} from 'sanity'

export const delivery = defineType({
  name: 'delivery',
  title: 'Delivery',
  type: 'document',
  fields: [
    defineField({
      name: 'newsletter',
      title: 'Newsletter Edition',
      description: 'The newsletter edition to be dispatched',
      type: 'reference',
      to: [{type: 'newsletterEdition'}],
      validation: (Rule) => Rule.required().error('Newsletter edition reference is required'),
    }),
    defineField({
      name: 'scheduledFor',
      title: 'Scheduled For',
      description: 'Date and time when the delivery queue should execute sending',
      type: 'datetime',
      validation: (Rule) => Rule.required().error('Scheduled delivery datetime is required'),
    }),
    defineField({
      name: 'status',
      title: 'Status',
      description: 'Dispatch delivery state',
      type: 'string',
      options: {
        list: [
          {title: 'Pending', value: 'pending'},
          {title: 'Scheduled', value: 'scheduled'},
          {title: 'Sending', value: 'sending'},
          {title: 'Sent', value: 'sent'},
          {title: 'Failed', value: 'failed'},
          {title: 'Cancelled', value: 'cancelled'},
        ],
      },
      initialValue: 'pending',
      validation: (Rule) =>
        Rule.required()
          .error('Status is required')
          .custom((val) => {
            const allowed = ['pending', 'scheduled', 'sending', 'sent', 'failed', 'cancelled']
            return (
              (val && allowed.includes(val as string)) ||
              `Status must be one of: ${allowed.join(', ')}`
            )
          }),
    }),
    defineField({
      name: 'sentAt',
      title: 'Sent At',
      description: 'Timestamp when delivery batch completed transmission',
      type: 'datetime',
    }),
    defineField({
      name: 'deliveryStats',
      title: 'Delivery Statistics',
      description: 'Aggregated metrics for email transmission',
      type: 'object',
      fields: [
        defineField({
          name: 'recipientCount',
          title: 'Recipient Count',
          description: 'Total subscribers targeted for delivery',
          type: 'number',
          validation: (Rule) => Rule.min(0).precision(0),
        }),
        defineField({
          name: 'deliveredCount',
          title: 'Delivered Count',
          description: 'Successfully confirmed deliveries',
          type: 'number',
          validation: (Rule) => Rule.min(0).precision(0),
        }),
        defineField({
          name: 'failedCount',
          title: 'Failed Count',
          description: 'Failed or bounced deliveries',
          type: 'number',
          validation: (Rule) => Rule.min(0).precision(0),
        }),
        defineField({
          name: 'lastUpdatedAt',
          title: 'Last Updated At',
          description: 'Timestamp when statistics were last synced from Herald delivery engine',
          type: 'datetime',
          initialValue: () => new Date().toISOString(),
        }),
      ],
    }),
  ],
  preview: {
    select: {
      newsletterTitle: 'newsletter.title',
      status: 'status',
      scheduledFor: 'scheduledFor',
    },
    prepare({newsletterTitle, status, scheduledFor}) {
      const dateStr = scheduledFor ? new Date(scheduledFor).toLocaleString() : 'Unscheduled'
      return {
        title: newsletterTitle ? `Delivery: ${newsletterTitle}` : 'Delivery Record',
        subtitle: `Status: ${status || 'pending'} • Scheduled: ${dateStr}`,
      }
    },
  },
})
