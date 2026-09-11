-- =======================================================
-- CREDITINSTA CHATBOT SCHEMA (NEW TABLES ONLY)
-- Safe to run: Links user_id to [dbo].[USERS]([ID])
-- Does NOT alter or modify any existing tables or columns.
-- =======================================================

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[chatbot_sessions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[chatbot_sessions] (
        [session_id] NVARCHAR(64) PRIMARY KEY,
        [user_id] INT NOT NULL,
        [title] NVARCHAR(255) DEFAULT 'New Conversation',
        [created_at] DATETIME2 DEFAULT SYSUTCDATETIME(),
        [updated_at] DATETIME2 DEFAULT SYSUTCDATETIME(),
        [is_active] BIT DEFAULT 1,
        CONSTRAINT [FK_chatbot_sessions_users] FOREIGN KEY ([user_id]) 
            REFERENCES [dbo].[USERS] ([ID]) ON DELETE CASCADE
    );

    CREATE INDEX [IX_chatbot_sessions_user_id] ON [dbo].[chatbot_sessions] ([user_id], [updated_at] DESC);
    PRINT 'Table chatbot_sessions created successfully with FK to USERS(ID).';
END
ELSE
BEGIN
    PRINT 'Table chatbot_sessions already exists.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[chatbot_messages]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[chatbot_messages] (
        [id] BIGINT IDENTITY(1,1) PRIMARY KEY,
        [session_id] NVARCHAR(64) NOT NULL,
        [sender] NVARCHAR(16) NOT NULL, -- 'user' or 'bot'
        [message_type] NVARCHAR(32) DEFAULT 'text', -- 'text', 'greeting', 'card'
        [message] NVARCHAR(MAX) NOT NULL,
        [created_at] DATETIME2 DEFAULT SYSUTCDATETIME(),
        CONSTRAINT [FK_chatbot_messages_session] FOREIGN KEY ([session_id]) 
            REFERENCES [dbo].[chatbot_sessions] ([session_id]) ON DELETE CASCADE
    );

    CREATE INDEX [IX_chatbot_messages_session_id] ON [dbo].[chatbot_messages] ([session_id], [created_at] ASC);
    PRINT 'Table chatbot_messages created successfully.';
END
ELSE
BEGIN
    PRINT 'Table chatbot_messages already exists.';
END
GO
