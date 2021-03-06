Ext.define('devilry.extjshelpers.RestfulSimplifiedEditPanelBase', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.restfulsimplified_editpanel_base',
    requires: ['devilry.extjshelpers.RestSubmit'],

    config: {
        /**
         * @cfg
         * The model we are editing.
         */
        model: undefined,

        /**
         * @cfg
         * A instance of the ``Ext.data.Model`` which should be loaded into the
         * form.
         */
        record: undefined,

        /**
         * @cfg
         * Show the extra-bar (sidebar) at the bottom? Defaults to ``false``,
         * which means that it will be at the right hand side. This bar contains
         * help and error messages.
         */
        extrabaronbottom: false
    },
    cls: 'editform',
    bodyCls: 'editform-body',

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);

        this.addEvents(
        /**
         * Fired when save is clicked. This may be when the record have been
         * saved successfully, or when the save button has been clicked
         * depending on the subclass.  By default this is fired when the save
         * button in clicked.
         */
        'saveSuccess');
    },

    initComponent: function() {
        this.errorlist = Ext.create('devilry.extjshelpers.ErrorList');
        this.model = Ext.ModelManager.getModel(this.model);

        this.editform.frame = false;
        if(this.editform.flex == undefined) {
            this.editform.flex = 15;
        }
        this.editform.border = 0;

        var extrabarCssCls = this.extrabaronbottom? 'extrabaronbottom': 'extrabaronright';
        Ext.apply(this, {
            layout: {
                type: (this.extrabaronbottom? 'vbox': 'hbox'),
                align: 'stretch'
            },

            items: [this.editform, {
                xtype: 'panel',
                frame: false,
                autoScroll: true,
                border: false,
                bodyCls: 'editform-sidebar ' + extrabarCssCls,
                flex: 5,
                items: [this.errorlist, {
                    xtype: 'box',
                    html: this.parseHelp()
                }]
            }]
        });
        this.dockedItems = [{
            xtype: 'toolbar',
            dock: 'bottom',
            ui: 'footer',
            defaults: {minWidth: 75},

            items: ['->', {
                xtype: 'button',
                text: 'Save',
                scale: 'large',
                iconCls: 'icon-save-32',
                listeners: {
                    scope: this,
                    click: this.onSave
                }
            }]
        }];
        this.callParent(arguments);

        if(this.record) {
            this.loadRecord();
        }
    },

    parseHelp: function() {
        if(!this.editform.help) {
            return '';
        }
        var help = '<section class="helpsection">';
        var me = this;
        var state = this.record == undefined? 'new': 'existing';
        Ext.Array.each(this.editform.help, function(helpobj) {
            if(Ext.typeOf(helpobj) === 'string') {
                helpobj = {text: helpobj};
            }
            if(helpobj.state == undefined || (helpobj.state == state)) {
                help += Ext.String.format('<p>{0}</p>', helpobj.text);
            }
        });
        return help + '</section>';
    },

    onSave: function() {
        if(this.editform.getForm().isValid()) {
            var record = Ext.ModelManager.create(this.editform.getForm().getValues(),
                                                 this.model);
            this.fireEvent('saveSucess', record);
        };
    },

    loadRecord: function() {
        this.editform.loadRecord(this.record);
    }
});
