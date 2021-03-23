# DataSpace

## Troubleshooting

### Dissertations

#### Removing Duplicates

From the DataSpace server environment:
```
bin/jr_dspace ruby/dspace-jruby/bin/idspace

java_import org.dspace.content.Item
item = DSpace.fromString('88435/dsp018623j1658')
item.getMetadataFirstValue('dc', 'title', nil, Item::ANY)
items = Java::OrgDspaceContent::Item.findByMetadataField(DSpace.context, '', '', '', nil)
```
