/** Panel to show StaticFeedback info and create new static feedbacks.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor', {
    extend: 'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditor',
    requires: [
        'devilry.gradeeditors.DraftEditorWindow',
        'devilry.gradeeditors.RestfulRegistryItem',
        'devilry.extjshelpers.assignmentgroup.CreateNewDeadlineWindow'
    ],

    config: {
        /**
         * @cfg
         * A {@link devilry.extjshelpers.SingleRecordContainer} for GradeEditor Config.
         */
        gradeeditor_config_recordcontainer: undefined,

        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        assignmentgroup_recordcontainer: undefined,
        assignmentgroupmodel: undefined,
        deadlinemodel: undefined
    },

    constructor: function(config) {
        return this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);

        this.staticfeedback_recordcontainer.addListener('setRecord', this.onSetStaticFeedbackRecordInEditor, this);

        var me = this;
        this.createButton = Ext.create('Ext.button.Button', {
            text: 'Edit feedback',
            //iconCls: 'icon-edit-32',
            hidden: false,
            scale: 'large',
            listeners: {
                scope: this,
                click: this.loadGradeEditor
            }
        });
        this.editToolbar.add(this.createButton);

        this.addListener('afterStoreLoadMoreThanZero', this.showCreateButton, this);

        if(this.delivery_recordcontainer.record) {
            this.onLoadDeliveryInEditor();
        }
        this.delivery_recordcontainer.addListener('setRecord', this.onLoadDeliveryInEditor, this);

        if(this.gradeeditor_config_recordcontainer.record) {
            this.onLoadGradeEditorConfig();
        }
        this.gradeeditor_config_recordcontainer.addListener('setRecord', this.onLoadGradeEditorConfig, this);

        this.registryitem_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.registryitem_recordcontainer.addListener('setRecord', this.onLoadRegistryItem, this);

        this.assignmentgroup_recordcontainer.addListener('setRecord', this.showCreateButton, this);

    },

    /**
     * @private
     * This is suffixed with InEditor to not crash with superclass.onLoadDelivery().
     */
    onLoadDeliveryInEditor: function() {
        this.showCreateButton();
    },

    /**
     * @private
     */
    onLoadGradeEditorConfig: function() {
        this.loadRegistryItem();
    },

    /**
     * @private
     */
    loadRegistryItem: function() {
        var registryitem_model = Ext.ModelManager.getModel('devilry.gradeeditors.RestfulRegistryItem');
        registryitem_model.load(this.gradeeditor_config_recordcontainer.record.data.gradeeditorid, {
            scope: this,
            success: function(record) {
                this.registryitem_recordcontainer.setRecord(record);
            }
        });
    },

    /**
     * @private
     */
    onLoadRegistryItem: function() {
        this.showCreateButton();
    },

    /**
     * @private
     * Show create button when:
     *
     * - Delivery has loaded.
     * - Grade editor config has loaded.
     * - Registry item has loaded.
     */
    showCreateButton: function() {
        if(this.gradeeditor_config_recordcontainer.record &&
                this.delivery_recordcontainer.record &&
                this.registryitem_recordcontainer.record &&
                this.assignmentgroup_recordcontainer.record) {
            //if(this.assignmentgroup_recordcontainer.record.data.is_open) {
                //this.createButton.show();
            //} else {
                //this.createButton.hide();
            //}
        }
    },

    /**
     * @private
     */
    loadGradeEditor: function() {
        Ext.widget('gradedrafteditormainwin', {
            deliveryid: this.delivery_recordcontainer.record.data.id,
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            listeners: {
                scope: this,
                publishNewFeedback: this.onPublishNewFeedback
            }
        }).show();
    },

    /**
     * Overrides parent method to enable examiners to click to create feedback.
     */
    bodyWithNoFeedback: function() {
        var me = this;
        this.setBody({
            xtype: 'component',
            cls: 'no-feedback-editable',
            html: '<p class="no-feedback-message">No feedback</p><p class="click-create-create-feedback-message">Click to create feedback</p>',
            listeners: {
                render: function() {
                    this.getEl().addListener('mouseup', me.loadGradeEditor, me);
                }
            }
        });
    },

    /**
     * @private
     */
    onPublishNewFeedback: function() {
        this.hasNewPublishedStaticFeedback = true;
        this.onLoadDelivery();
    },

    /**
     * @private
     */
    onSetStaticFeedbackRecordInEditor: function() {
        if(this.hasNewPublishedStaticFeedback) {
            this.hasNewPublishedStaticFeedback = false;
            this.onNewPublishedStaticFeedback();
        }
    },

    /**
     * @private
     */
    onNewPublishedStaticFeedback: function() {
        var staticfeedback = this.staticfeedback_recordcontainer.record.data;
        if(staticfeedback.is_passing_grade) {
            this.reloadAssignmentGroup();
        } else {
            this.onFailingGrade();
        }
    },

    /**
     * @private
     */
    reloadAssignmentGroup: function() {
        this.assignmentgroupmodel.load(this.assignmentgroup_recordcontainer.record.data.id, {
            scope: this,
            success: function(record) {
                this.assignmentgroup_recordcontainer.setRecord(record);
            },
            failure: function() {
                // TODO: Handle errors
            }
        });
    },

    /**
     * @private
     */
    onFailingGrade: function() {
        var win = Ext.MessageBox.show({
            title: 'You published a feedback with a failing grade',
            msg: '<p>Would you like to give the group another try?</p><ul>' +
                '<li>Choose <strong>yes</strong> to create a new deadline</li>' +
                '<li>Choose <em>no</no> to close the group. This fails the student on this assignment. You can re-open the group at any time.</li>' +
                '</ul>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this.createNewDeadline();
                } else {
                    this.reloadAssignmentGroup();
                }
            }
        });
    },

    /**
     * @private
     */
    createNewDeadline: function() {
        var me = this;
        var createDeadlineWindow = Ext.widget('createnewdeadlinewindow', {
            assignmentgroupid: this.assignmentgroup_recordcontainer.record.data.id,
            deadlinemodel: this.deadlinemodel,
            onSaveSuccess: function(record) {
                me.reloadAssignmentGroup();
                this.close();
            }
        });
        createDeadlineWindow.show();
    }
});
