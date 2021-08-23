CREATE TABLE "standing_order" (
	"id"	INTEGER NOT NULL,
	"payer"	VARCHAR(80) NOT NULL,
	"amount"	FLOAT NOT NULL,
	"comment"	VARCHAR(80) NOT NULL,
	"creation_timestamp"	INTEGER NOT NULL,
	"last_execution"	INTEGER,
	"group_id"	INTEGER NOT NULL,
	"creator_id"	INTEGER NOT NULL,
	"cron_expression"	VARCHAR(80) NOT NULL,
	"periodicity"	VARCHAR(80) NOT NULL,
	FOREIGN KEY("creator_id") REFERENCES "user"("id"),
	FOREIGN KEY("group_id") REFERENCES "group"("id"),
	PRIMARY KEY("id")
);

CREATE TABLE "standing_order_involved" (
	"id"	INTEGER NOT NULL,
	"participant"	VARCHAR(80) NOT NULL,
	"standing_order_id"	INTEGER NOT NULL,
	FOREIGN KEY("standing_order_id") REFERENCES "standing_order"("id") ON DELETE CASCADE,
	PRIMARY KEY("id")
);
