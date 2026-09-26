import {defineType, defineField} from 'sanity'

export const theme = defineType({
  name: 'theme',
  title: 'Theme',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      description: 'Name of the parish or liturgical theme',
      type: 'string',
      validation: (Rule) => Rule.required().error('Theme name is required'),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      description: 'Brief description of the theme and its parish context',
      type: 'text',
      rows: 3,
    }),
    defineField({
      name: 'category',
      title: 'Category',
      description: 'Liturgical or parish ministry category',
      type: 'string',
      options: {
        list: [
          {title: 'Spiritual', value: 'spiritual'},
          {title: 'Community', value: 'community'},
          {title: 'Service', value: 'service'},
          {title: 'Stewardship', value: 'stewardship'},
          {title: 'Vocation', value: 'vocation'},
          {title: 'Social', value: 'social'},
          {title: 'Liturgy', value: 'liturgy'},
          {title: 'Parish', value: 'parish'},
        ],
      },
      validation: (Rule) =>
        Rule.custom((val) => {
          if (!val) return true
          const allowed = [
            'spiritual',
            'community',
            'service',
            'stewardship',
            'vocation',
            'social',
            'liturgy',
            'parish',
          ]
          return allowed.includes(val as string) || `Category must be one of: ${allowed.join(', ')}`
        }),
    }),
  ],
  preview: {
    select: {
      title: 'name',
      category: 'category',
    },
    prepare({title, category}) {
      return {
        title: title || 'Untitled Theme',
        subtitle: category ? `Category: ${category}` : undefined,
      }
    },
  },
})
