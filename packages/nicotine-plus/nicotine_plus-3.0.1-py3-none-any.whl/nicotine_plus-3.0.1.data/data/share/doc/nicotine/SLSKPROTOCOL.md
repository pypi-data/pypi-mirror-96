# Soulseek Protocol Documentation

Last updated on February 19, 2020

## Sections

- [Packing](#packing)
- [Constants](#constants)
- [Server Messages](#server-messages)
- [Peer Messages](#peer-messages)
- [Distributed Messages](#distributed-messages)
- [Museek Data Types](#museek-data-types)

# Packing

### String

| Length of String | String |
| ---------------- | ------ |
| 4 Byte           | String |

### Integer

| Number |
| ------ |
| 4 Byte |

### Large Integer

| Number |
| ------ |
| 8 Byte |

### Bool

| Character |
| --------- |
| 1 Byte    |

# Constants

### Connection Types

| Type | Connection          |
| ---- | ------------------- |
| P    | Peer To Peer        |
| F    | File Transfer       |
| D    | Distributed Network |

### Status Codes

| Code | Status  |
| ---- | ------- |
| -1   | Unknown |
| 0    | Offline |
| 1    | Away    |
| 2    | Online  |

### Transfer Direction

| Code | Type     |
| ---- | -------- |
| 0    | Download |
| 1    | Upload   |

# Server Messages

| Send           | Receive             |
| -------------- | ------------------- |
| Send to Server | Receive from Server |

These messages are used by clients to interface with the server.
Internal Server messages are spooky and not understood, since the OSS
crowd doesn't have access to its source code. If you want a Soulseek
server, check out
[Soulfind](https://github.com/seeschloss/soulfind).
Soulfind is obviously not the exact same the official Soulseek server,
but it handles the protocol well enough (and can be modified).

In museekd 0.1.13, these messages are sent and received in
Museek/ServerConnection.cc and defined in Museek/ServerMessages.hh.
Since museekd 0.2, they are defined in museekd/servermessages.h.

In Nicotine, these messages are matched to their message number in
slskproto.py in the SlskProtoThread function, defined in slskmessages.py
and callbacks for the messages are set in pynicotine.py.

#### The Server Message format

| Message Length | Code    | Message Contents |
| -------------- | ------- | ---------------- |
| 4 Bytes        | 4 Bytes | ...              |

#### Message Index

| Code | Message                                           | Status     |
| ---- | ------------------------------------------------- | ---------- |
| 1    | [Login](#server-code-1)                           |            |
| 2    | [Set Listen Port](#server-code-2)                 |            |
| 3    | [Get Peer Address](#server-code-3)                |            |
| 5    | [Add User](#server-code-5)                        |            |
| 6    | [Remove User](#server-code-6)                     |            |
| 7    | [Get Status](#server-code-7)                      |            |
| 13   | [Say in Chat Room](#server-code-13)               |            |
| 14   | [Join Room](#server-code-14)                      |            |
| 15   | [Leave Room](#server-code-15)                     |            |
| 16   | [User Joined Room](#server-code-16)               |            |
| 17   | [User Left Room](#server-code-17)                 |            |
| 18   | [Connect To Peer](#server-code-18)                |            |
| 22   | [Private Messages](#server-code-22)               |            |
| 23   | [Acknowledge Private Message](#server-code-23)    |            |
| 26   | [File Search](#server-code-26)                    |            |
| 28   | [Set Online Status](#server-code-28)              |            |
| 32   | [Ping](#server-code-32)                           | Deprecated |
| 33   | [Send Connect Token](#server-code-33)             | Deprecated |
| 34   | [Send Download Speed](#server-code-34)            | Deprecated |
| 35   | [Shared Folders & Files](#server-code-35)         |            |
| 36   | [Get User Stats](#server-code-36)                 |            |
| 40   | [Queued Downloads](#server-code-40)               | Deprecated |
| 41   | [Kicked from Server](#server-code-41)             |            |
| 42   | [User Search](#server-code-42)                    |            |
| 51   | [Interest Add](#server-code-51)                   |            |
| 52   | [Interest Remove](#server-code-52)                |            |
| 54   | [Get Recommendations](#server-code-54)            |            |
| 56   | [Get Global Recommendations](#server-code-56)     |            |
| 57   | [Get User Interests](#server-code-57)             |            |
| 58   | [Admin Command](#server-code-58)                  |            |
| 60   | [Place In Line Response](#server-code-60)         | Deprecated |
| 62   | [Room Added](#server-code-62)                     | Deprecated |
| 63   | [Room Removed](#server-code-63)                   | Deprecated |
| 64   | [Room List](#server-code-64)                      |            |
| 65   | [Exact File Search](#server-code-65)              | Deprecated |
| 66   | [Global/Admin Message](#server-code-66)           |            |
| 67   | [Global User List](#server-code-67)               | Deprecated |
| 68   | [Tunneled Message](#server-code-68)               | Deprecated |
| 69   | [Privileged Users](#server-code-69)               |            |
| 71   | [Have No Parents](#server-code-71)                |            |
| 73   | [Parent's IP](#server-code-73)                    |            |
| 83   | [Parent Min Speed](#server-code-83)               |            |
| 84   | [Parent Speed Ratio](#server-code-84)             |            |
| 86   | [Parent Inactivity Timeout](#server-code-86)      | Deprecated |
| 87   | [Search Inactivity Timeout](#server-code-87)      | Deprecated |
| 88   | [Minimum Parents In Cache](#server-code-88)       | Deprecated |
| 90   | [Distributed Alive Interval](#server-code-90)     | Deprecated |
| 91   | [Add Privileged User](#server-code-91)            |            |
| 92   | [Check Privileges](#server-code-92)               |            |
| 93   | [Search Request](#server-code-93)                 |            |
| 100  | [Accept Children](#server-code-100)               |            |
| 102  | [Possible Parents](#server-code-102)              |            |
| 103  | [Wishlist Search](#server-code-103)               |            |
| 104  | [Wishlist Interval](#server-code-104)             |            |
| 110  | [Get Similar Users](#server-code-110)             |            |
| 111  | [Get Item Recommendations](#server-code-111)      |            |
| 112  | [Get Item Similar Users](#server-code-112)        |            |
| 113  | [Room Tickers](#server-code-113)                  |            |
| 114  | [Room Ticker Add](#server-code-114)               |            |
| 115  | [Room Ticker Remove](#server-code-115)            |            |
| 116  | [Set Room Ticker](#server-code-116)               |            |
| 117  | [Hated Interest Add](#server-code-117)            |            |
| 118  | [Hated Interest Remove](#server-code-118)         |            |
| 120  | [Room Search](#server-code-120)                   |            |
| 121  | [Send Upload Speed](#server-code-121)             |            |
| 122  | [User Privileges](#server-code-122)               |            |
| 123  | [Give Privileges](#server-code-123)               |            |
| 124  | [Notify Privileges](#server-code-124)             |            |
| 125  | [Acknowledge Notify Privileges](#server-code-125) |            |
| 126  | [Branch Level](#server-code-126)                  |            |
| 127  | [Branch Root](#server-code-127)                   |            |
| 129  | [Child Depth](#server-code-129)                   |            |
| 133  | [Private Room Users](#server-code-133)            |            |
| 134  | [Private Room Add User](#server-code-134)         |            |
| 135  | [Private Room Remove User](#server-code-135)      |            |
| 136  | [Private Room Drop Membership](#server-code-136)  |            |
| 137  | [Private Room Drop Ownership](#server-code-137)   |            |
| 138  | [Private Room Unknown](#server-code-138)          |            |
| 139  | [Private Room Added](#server-code-139)            |            |
| 140  | [Private Room Removed](#server-code-140)          |            |
| 141  | [Private Room Toggle](#server-code-141)           |            |
| 142  | [New Password](#server-code-142)                  |            |
| 143  | [Private Room Add Operator](#server-code-143)     |            |
| 144  | [Private Room Remove Operator](#server-code-144)  |            |
| 145  | [Private Room Operator Added](#server-code-145)   |            |
| 146  | [Private Room Operator Removed](#server-code-146) |            |
| 148  | [Private Room Owned](#server-code-148)            |            |
| 149  | [Message Users](#server-code-149)                 |            |
| 150  | [Ask Public Chat](#server-code-150)               |            |
| 151  | [Stop Public Chat](#server-code-151)              |            |
| 152  | [Public Chat Message](#server-code-152)           |            |
| 153  | [Related Searches](#server-code-153)              | Deprecated |
| 1001 | [Can't Connect To Peer](#server-code-1001)        | Deprecated |
| 1003 | [Can't Create Room](#server-code-1003)            |            |

### Server Code 1

**Login**

#### Function Names

Museekd: SLogin  
Nicotine: Login

#### Description

Send your username, password, and client version.

##### Sending Login Example

| Description | Message Length | Message Code | Username Length | Username                | Password Length | Password                |
| ----------- | -------------- | ------------ | --------------- | ----------------------- | --------------- | ----------------------- |
| Human       | 72             | 1            | 8               | username                | 8               | password                |
| Hex         | 48 00 00 00    | 01 00 00 00  | 08 00 00 00     | 75 73 65 72 6e 61 6d 65 | 08 00 00 00     | 70 61 73 73 77 6f 72 64 |

*Message, continued*

| Description | Version     | Length      | Hash                                                                                            | Minor Version |
| ----------- | ----------- | ----------- | ----------------------------------------------------------------------------------------------- | ------------- |
| Human       | 160         | 32          | d51c9a7e9353746a6020f9602d452929                                                                | 1             |
| Hex         | a0 00 00 00 | 20 00 00 00 | 64 35 31 63 39 61 37 65 39 33 35 33 37 34 36 61 36 30 32 30 66 39 36 30 32 64 34 35 32 39 32 39 | 01 00 00 00   |

*Message as a Hex Stream* **48 00 00 00 01 00 00 00 08 00 00 00 75 73 65
72 6e 61 6d 65 08 00 00 00 70 61 73 73 77 6f 72 64 a0 00 00 00 20 00 00
00 64 35 31 63 39 61 37 65 39 33 35 33 37 34 36 61 36 30 32 30 66 39 36
30 32 64 34 35 32 39 32 39 01 00 00 00**

#### Data Order

  - Send Login
    1.  **string** <ins>username</ins>
    2.  **string** <ins>password</ins> **A non-empty
        string is required**
    3.  **uint32** <ins>version number</ins> *183*
        for Museek+ *160* for Nicotine+
    4.  **string** <ins>MD5 hex digest of
        concatenated username & password</ins>
    5.  **uint32** <ins>minor version</ins> Minor
        version (0x13000000 for 157 ns 13e, 0x11000000 for 157 ns 13c)

<!-- end list -->

  - Receive Login Success
    1.  **uchar** <ins>success</ins> 1
    2.  **string** <ins>greet</ins> A MOTD string
    3.  **uint32** <ins>Your IP Address</ins>
    4.  **string** <ins>MD5 hex digest of the
        password string</ins> *Windows Soulseek uses this hash to
        determine if it's connected to the official server*

<!-- end list -->

  - Receive Login Failure
    1.  **uchar** <ins>failure</ins> *0*
    2.  **string** <ins>reason</ins> Almost always:
        *Bad Password*; sometimes it's a banned message or another
        error.

### Server Code 2

**Set Listen Port**

#### Function Names

Museekd: SSetListenPort  
Nicotine: SetWaitPort

#### Description

We send this to the server to indicate the port number that we listen on (2234 by default).

#### Data Order

  - Send
    1.  **uint32** <ins>port</ins>
  - Receive
      - *No Message*

### Server Code 3

**Get Peer Address**

#### Function Names

Museekd: SGetPeerAddress  
Nicotine: GetPeerAddress

#### Description

We send this to the server to ask for a peer's address (IP address and port), given the peer's username.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **ip** <ins>ip</ins>
    3.  **int** <ins>port</ins>

### Server Code 5

**Add User**

#### Function Names

Museekd: SAddUser  
Nicotine: AddUser

#### Description

Used to be kept updated about a user's stats. When a user's stats have changed, the server sends a GetUserStats response message with the new user stats.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **char** <ins>exists</ins> *converted to
        Boolean*
    <!-- end list -->
      - If <ins>exists</ins> is 1/True (may not be
        implemented)
        1.  **int** <ins>status</ins> *0 == Offline,
            1 == Away; 2 == Online*
        2.  **int** <ins>avgspeed</ins>
        3.  **off\_t** <ins>downloadnum</ins>
        4.  **int** <ins>files</ins>
        5.  **int** <ins>dirs</ins>
        6.  **string** <ins>Country Code</ins> (may
            not be implemented)

### Server Code 6

**Remove User**

#### Function Names

Museekd: Unimplemented  
Nicotine: RemoveUser

#### Description

Used when we no longer want to be kept updated about a user's stats.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
      - *No Message*

### Server Code 7

**Get Status**

#### Function Names

Museekd: SGetStatus  
Nicotine: GetUserStatus

#### Description

The server tells us if a user has gone away or has returned.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>status</ins> *0 == Offline, 1
        == Away; 2 == Online*
    3.  **bool** <ins>privileged</ins>

### Server Code 13

**Say in Chat Room**

#### Function Names

Museekd: SSayChatroom  
Nicotine: SayChatroom

#### Description

Either we want to say something in the chatroom, or someone else did.

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>message</ins>
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
    3.  **string** <ins>message</ins>

### Server Code 14

**Join a Room**

#### Function Names

Museekd: SJoinRoom  
Nicotine: JoinRoom

#### Description

We send this message to the server when we want to join a room. If the room doesn't exist, it is created.

Server responds with this message when we join a room. Contains users list with data on everyone.

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **bool** <ins>private</ins> *If the room doesn't exist, should the new room be private?*

<!-- end list -->

  - Receive
    1.  **string** <ins>room</ins>
    2.  **int** <ins>number of users in room</ins>
        **For private rooms, also contain owner and operators**
    3.  Iterate the <ins>number of users</ins>
        **museekd uses a vector of strings**
        1.  **string** <ins>username</ins>
    4.  **int** <ins>number of userdata</ins>
    5.  Iterate the <ins>number of users</ins>
        **museekd uses a vector of userdata**
        1.  **int** <ins>status</ins>
    6.  **int** <ins>number of userdata</ins>
    7.  Iterate the userdata **vector of userdata** (and add unpacked
        data to [User Data](#user-data))
        1.  **int** <ins>avgspeed</ins>
        2.  **off\_t** <ins>downloadnum</ins>
        3.  **int** <ins>files</ins>
        4.  **int** <ins>dirs</ins>
    8.  **int** <ins>number of slotsfree</ins>
    9.  Iterate thru number of slotsfree
        1.  **int** <ins>slotsfree</ins>
    10. **int** <ins>number of usercountries</ins>
    11. Iterate thru number of usercountries
        1.  **string** <ins>countrycode</ins>
            **Uppercase country code**
    12. **string** <ins>owner</ins> **If private
        room**
    13. **int** <ins>number of operators in
        room</ins> **If private room**
    14. Iterate the <ins>number of operators</ins>
        **museekd uses a vector of strings**
        1.  **string** <ins>operator</ins>

### Server Code 15

**Leave Room**

#### Function Names

Museekd: SLeaveRoom  
Nicotine: LeaveRoom

#### Description

We send this to the server when we want to leave a room.

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 16

**A User Joined a Room**

#### Function Names

Museekd: SUserJoinedRoom  
Nicotine: UserJoinedRoom

#### Description

The server tells us someone has just joined a room we're in.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
    3.  **int** <ins>status</ins>
    4.  **int** <ins>avgspeed</ins>
    5.  **off\_t** <ins>downloadnum</ins>
    6.  **int** <ins>files</ins>
    7.  **int** <ins>dirs</ins>
    8.  **int** <ins>slotsfree</ins>
    9.  **string** <ins>countrycode</ins>\_
        **Uppercase country code**

### Server Code 17

**A User Left a Room**

#### Function Names

Museekd: SUserLeftRoom  
Nicotine: UserLeftRoom

#### Description

The server tells us someone has just left a room we're in.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>

### Server Code 18

**Connect To Peer**

#### Function Names

Museekd: SConnectToPeer  
Nicotine: ConnectToPeer

#### Description

Either we ask server to tell someone else we want to establish a connection with them, or server tells us someone wants to connect with us. Used when the side that wants a connection can't establish it, and tries to go the other way around (direct connection has failed).

See also: [Peer
Connection Message
Order](#peer-connection-message-order)

#### Data Order

  - Send
    1.  **uint32** <ins>token</ins>
    2.  **string** <ins>username</ins>
    3.  **string** <ins>type</ins> *Connection Type
        (P, F or D)*
  - Receive
    1.  **string** <ins>username</ins>
    2.  **string** <ins>type</ins> *Connection Type
        (P, F or D)*
    3.  **ip** <ins>ip</ins>
    4.  **int** <ins>port</ins>
    5.  **uint32** <ins>token</ins> *Use this token
        for [Pierce Firewall](#peer-code-0)*
    6.  **bool** <ins>privileged</ins>

### Server Code 22

**Private Messages**

#### Function Names

Museekd: SPrivateMessage  
Nicotine: MessageUser

#### Description

Chat phrase sent to someone or received by us in private.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **string** <ins>message</ins>
  - Receive
    1.  **int** <ins>ID</ins>
    2.  **int** <ins>timestamp</ins>
    3.  **string** <ins>username</ins>
    4.  **string** <ins>message</ins>
    5.  **bool** <ins>new message</ins> **1 if message is new, 0 if message is re-sent (e.g. if recipient was offline)**

### Server Code 23

**Acknowledge Private Message**

#### Function Names

Museekd: SAckPrivateMessage  
Nicotine: MessageAcked

#### Description

We send this to the server to confirm that we received a private message. If we don't send it, the server will keep sending the chat phrase to us.

Museekd also resets timestamps to account for server-time bugginess.

#### Data Order

  - Send
    1.  **int** <ins>message ID</ins>
  - Receive
      - *No Message*

### Server Code 26

**File Search**

#### Function Names

Museekd: SFileSearch  
Nicotine: FileSearch

#### Description

We send this to the server when we search for something. Alternatively, the server sends this message to tell us that someone is searching for something.

The ticket/search id is a random number generated by the client and is used to track the search results.

#### Data Order

  - Send
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>search query</ins>
  - Receive *search request from another user*
    1.  **string** <ins>username</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>search query</ins>

### Server Code 28

**Set Online Status**

#### Function Names

Museekd: SSetStatus  
Nicotine: SetStatus

#### Description

We send our new status to the server. Status is a way to define whether you're available or busy. 

*-1 = Unknown  
0 = Offline  
1 = Away  
2 = Online*

#### Data Order

  - Send
    1.  **int** <ins>status</ins>
  - Receive
      - *No Message*

### Server Code 32

**Ping**

#### Function Names

Museekd: SPing  
Nicotine: ServerPing

#### Description

**DEPRECATED**

We test if the server responds.

#### Data Order

  - Send
      - Empty Message
  - Receive
      - Empty Message

### Server Code 33

**Send Connect Token**

#### Function Names

Museekd: Unimplemented  
Nicotine: SendConnectToken

#### Description

**DEPRECATED**

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **int** <ins>token</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>token</ins>

### Server Code 34

**Send Download Speed**

#### Function Names

Museekd: SSendSpeed  
Nicotine: SendDownloadSpeed

#### Description

**DEPRECATED**

We used to send this after a finished download to let the server update the speed statistics for a user.

#### Data Order

  - Send *average transfer speed*
    1.  **string** <ins>username</ins>
    2.  **int** <ins>speed</ins>
  - Receive
      - *No Message*

### Server Code 35

**Shared Folders & Files**

#### Function Names

Museekd: SSharedFoldersFiles  
Nicotine: SharedFoldersFiles

#### Description

We send this to server to indicate the number of folder and files that we share.

#### Data Order

  - Send
    1.  **int** <ins>dirs</ins>
    2.  **int** <ins>files</ins>
  - Receive
      - *No Message*

### Server Code 36

**Get User Stats**

#### Function Names

Museekd: SGetUserStats  
Nicotine: GetUserStats

#### Description

The server sends this to indicate a change in a user's statistics, if we've requested to watch the user in AddUser previously. A user's stats can also be requested by sending a GetUserStats message to the server, but AddUser should be used instead.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>avgspeed</ins>
    3.  **off\_t** <ins>downloadnum</ins>
    4.  **int** <ins>files</ins>
    5.  **int** <ins>dirs</ins>

### Server Code 40

**Queued Downloads**

#### Function Names

Museekd: Unimplemented  
Nicotine: QueuedDownloads

#### Description

**DEPRECATED**

The server sends this to indicate if someone has download slots available or not.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>username</ins>
    2.  **bool** <ins>slotsfree</ins> *Can
        immediately download*

### Server Code 41

**Kicked from Server**

#### Function Names

Museekd: SKicked  
Nicotine: Relogged

#### Description

The server sends this if someone else logged in under our nickname, and then disconnects us.

#### Data Order

  - Send
      - *No Message*
  - Receive
      - Empty Message

### Server Code 42

**User Search**

#### Function Names

Museekd: SUserSearch  
Nicotine: UserSearch

#### Description

We send this to the server when we search a specific user's shares. The ticket/search id is a random number generated by the client and is used to track the search results.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>search query</ins>
  - Receive
      - *No Message*

### Server Code 51

**Add Liked Interest**

#### Function Names

Museekd: SInterestAdd  
Nicotine: AddThingILike

#### Description

We send this to the server when we add an item to our likes list.

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 52

**Remove Liked Interest**

#### Function Names

Museekd: SInterestRemove  
Nicotine: RemoveThingILike

#### Description

We send this to the server when we remove an item from our likes list.

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 54

**Get Recommendations**

#### Function Names

Museekd: SGetRecommendations  
Nicotine: Recommendations

#### Description

The server sends us a list of personal recommendations and a number for each.

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of total
        recommendations</ins>
    2.  Iterate for <ins>number of total
        recommendations</ins>
        1.  **string** <ins>recommendation</ins>
        2.  **int** <ins>number of recommendations
            this recommendation has</ins>
    3.  **int** <ins>number of total
        unrecommendations</ins>
    4.  Iterate for <ins>number of total
        unrecommendations</ins>
        1.  **string** <ins>unrecommendation</ins>
        2.  **int** <ins>number of unrecommendations
            this unrecommendation has (negative)</ins>

### Server Code 56

**Get Global Recommendations**

#### Function Names

Museekd: SGetGlobalRecommendations  
Nicotine: GlobalRecommendations

#### Description

The server sends us a list of global recommendations and a number for each.

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of total
        recommendations</ins>
    2.  Iterate for <ins>number of total
        recommendations</ins>
        1.  **string** <ins>recommendation</ins>
        2.  **int** <ins>number of recommendations
            this recommendation has</ins>
    3.  **int** <ins>number of total
        unrecommendations</ins>
    4.  Iterate for <ins>number of total
        unrecommendations</ins>
        1.  **string** <ins>unrecommendation</ins>
        2.  **int** <ins>number of unrecommendations
            this unrecommendation has (negative)</ins>

### Server Code 57

**Get User Interests**

#### Function Names

Museekd: SUserInterests  
Nicotine: UserInterests

#### Description

We ask the server for a user's liked and hated interests. The server responds with a list of interests.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>number of liked interests</ins>
    3.  Iterate for <ins>number of liked
        interests</ins>
        1.  **string** <ins>interest</ins>
    4.  **int** <ins>number of hated interests</ins>
    5.  Iterate for <ins>number of hated
        interests</ins>
        1.  **string** <ins>interest</ins>

### Server Code 58

**Admin Command**

#### Function Names

Museekd: Unimplemented  
Nicotine: AdminCommand

#### Description

#### Data Order

  - Send
    1.  **string** <ins>string</ins>
    2.  **int** <ins>number of strings</ins>
    3.  Iterate for <ins>number of strings</ins>
        1.  **string** <ins>string</ins>
  - Receive
      - *No Message*

### Server Code 60

**Place In Line Response**

#### Description

**DEPRECATED**

The server tells us a new room has been added.

#### Function Names

Museekd: Unimplemented  
Nicotine: PlaceInLineResponse

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **int** <ins>req</ins>
    3.  **int** <ins>place</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>req</ins>
    3.  **int** <ins>place</ins>

### Server Code 62

**Room Added**

#### Description

**DEPRECATED**

The server tells us a new room has been added.

#### Function Names

Museekd: Unimplemented  
Nicotine: RoomAdded

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 63

**Room Removed**

#### Description

**DEPRECATED**

The server tells us a room has been removed.

#### Function Names

Museekd: Unimplemented  
Nicotine: RoomRemoved

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 64

**Room List**

#### Function Names

Museekd: SRoomList  
Nicotine: RoomList

#### Description

The server tells us a list of rooms and the number of users in them. When connecting to the server, the server only sends us rooms with at least 5 users. A few select rooms are also excluded, such as nicotine and The Lobby. Requesting the room list yields a response containing the missing rooms.

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of rooms</ins>
    2.  Iterate for <ins>number of rooms</ins>
        1.  **string** <ins>room</ins>
    3.  **int** <ins>number of rooms</ins>
    4.  Iterate for <ins>number of rooms</ins>
        1.  **int** <ins>number of users in
            room</ins>

<!-- end list -->

1.  **int** <ins>number of owned private rooms</ins>
2.  Iterate for <ins>number of owned private
    rooms</ins>
    1.  **string** <ins>owned private room</ins>
3.  **int** <ins>number of owned private rooms</ins>
4.  Iterate for <ins>number of owned private
    rooms</ins>
    1.  **int** <ins>number of users in owned private
        room</ins>

<!-- end list -->

1.  **int** <ins>number of private rooms (except
    owned)</ins>
2.  Iterate for <ins>number of private rooms (except
    owned)</ins>
    1.  **string** <ins>private room</ins>
3.  **int** <ins>number of private rooms (except
    owned)</ins>
4.  Iterate for <ins>number of private rooms (except
    owned)</ins>
    1.  **int** <ins>number of users in private rooms
        (except owned)</ins>

<!-- end list -->

1.  **int** <ins>number of operated private
    rooms</ins>
2.  Iterate for <ins>number of operated private
    rooms</ins>
    1.  **string** <ins>operated private room</ins>

### Server Code 65

**Exact File Search**

#### Function Names

Museekd: SExactFileSearch  
Nicotine: ExactFileSearch

#### Description

**DEPRECATED (no results even with official client)**

We send this to search for an exact file name and folder, to find other sources.

#### Data Order

  - Send
    1.  **uint32** <ins>token</ins>
    2.  **string** <ins>filename</ins>
    3.  **string** <ins>path</ins>
    4.  **off\_t** <ins>filesize</ins>
    5.  **uint32** <ins>checksum</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **uint32** <ins>token</ins>
    3.  **string** <ins>filename</ins>
    4.  **string** <ins>path</ins>
    5.  **off\_t** <ins>filesize</ins>
    6.  **uint32** <ins>checksum</ins>

### Server Code 66

**Global / Admin Message**

#### Function Names

Museekd: SGlobalMessage  
Nicotine: AdminMessage

#### Description

A global message from the server admin has arrived.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>message</ins>

### Server Code 67

**Global User List**

#### Function Names

Museekd: Unimplemented  
Nicotine: GlobalUserList

#### Description

**DEPRECATED**

We send this to get a global list of all users online.

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of users in room</ins>
    2.  Iterate the <ins>number of users</ins>
        1.  **string** <ins>username</ins>
    3.  **int** <ins>number of userdata</ins>
    4.  Iterate the <ins>number of users</ins>
        1.  **int** <ins>status</ins>
    5.  **int** <ins>number of userdata</ins>
    6.  Iterate the <ins>userdata</ins>
        1.  **int** <ins>avgspeed</ins>
        2.  **off\_t** <ins>downloadnum</ins>
        3.  **int** <ins>files</ins>
        4.  **int** <ins>dirs</ins>
    7.  **int** <ins>number of slotsfree</ins>
    8.  Iterate thru number of slotsfree
        1.  **int** <ins>slotsfree</ins>
    9. **int** <ins>number of usercountries</ins>
    10. Iterate thru number of usercountries
        1.  **string** <ins>countrycode</ins>
            **Uppercase country code**

### Server Code 68

**Tunneled Message**

#### Function Names

Museekd: Unimplemented  
Nicotine: TunneledMessage

#### Description

**DEPRECATED**

Server message for tunneling a chat message.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **int** <ins>token</ins>
    3.  **int** <ins>code</ins>
    4.  **string** <ins>message</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **int** <ins>code</ins>
    3.  **int** <ins>token</ins>
    4.  **ip** <ins>ip</ins>
    5.  **int** <ins>port</ins>
    6.  **string** <ins>message</ins>

### Server Code 69

**Privileged Users**

#### Function Names

Museekd: SPrivilegedUsers  
Nicotine: PrivilegedUsers

#### Description

The server sends us a list of privileged users, a.k.a. users who have donated.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number of users</ins>
    2.  Iterate <ins>number of users</ins>
        1.  **string** <ins>username</ins>

### Server Code 71

**Have No Parents**

#### Function Names

Museekd: SHaveNoParents  
Nicotine: HaveNoParent

#### Description

We inform the server if we have a distributed parent or not. If not, the server eventually sends us a PossibleParents message with a list of 10 possible parents to connect to.

#### Data Order

  - Send
    1.  **bool** <ins>have\_parents</ins> (is a
        boolean internal to museekd)
  - Receive
      - *No Message*

### Server Code 73

**Parent's IP**

#### Function Names

Museekd: SParentIP  
Nicotine: SearchParent

#### Description

We send the IP address of our parent to the server.

#### Data Order

  - Send
    1.  **ip** <ins>ip</ins>
  - Receive
      - *No Message*

### Server Code 83

**Parent Min Speed**

#### Description

Unknown purpose

#### Function Names

Museekd: SParentMinSpeed  
Nicotine: ParentMinSpeed (unused)

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 84

**Parent Speed Ratio**

#### Description

Unknown purpose

#### Function Names

Museekd: SParentSpeedRatio  
Nicotine: ParentSpeedRatio (unused)

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 86

**Parent Inactivity Timeout**

#### Description

**DEPRECATED**

#### Function Names

Museekd: SParentInactivityTimeout  
Nicotine: ParentInactivityTimeout

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 87

**Search Inactivity Timeout**

#### Description

**DEPRECATED**

#### Function Names

Museekd: SSearchInactivityTimeout  
Nicotine: SearchInactivityTimeout

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 88

**Minimum Parents In Cache**

#### Description

**DEPRECATED**

#### Function Names

Museekd: SMinParentsInCache  
Nicotine: MinParentsInCache

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 90

**Distributed Alive Interval**

#### Description

**DEPRECATED**

#### Function Names

Museekd: SDistribAliveInterval  
Nicotine: DistribAliveInterval

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>number</ins>

### Server Code 91

**Add Privileged User**

#### Function Names

Museekd: SAddPrivileged  
Nicotine: AddToPrivileged

#### Description

The server sends us the username of a new privileged user, which we add to our list of global privileged users.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>username</ins>

### Server Code 92

**Check Privileges**

#### Function Names

Museekd: SCheckPrivileges  
Nicotine: CheckPrivileges

#### Description

We ask the server how much time we have left of our privileges. The server responds with the remaining time, in seconds.

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>time\_left</ins>

### Server Code 93

**Search Request**

#### Description

The server sends us search requests from other users.

#### Function Names

Museekd: SSearchRequest  
Nicotine: SearchRequest

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **uint8** <ins>distributed code
        (DSearchRequest)</ins>
    2.  **int** <ins>unknown</ins>
    3.  **string** <ins>username</ins>
    4.  **int** <ins>token</ins>
    5.  **string** <ins>query</ins>

### Server Code 100

**Accept Children**

#### Description

We tell the server if we want to accept child nodes.

#### Function Names

Museekd: SAcceptChildren  
Nicotine: AcceptChildren (not yet used)

#### Data Order

  - Send
    1.  **bool** <ins>accept</ins>
  - Receive
      - *No Message*

### Server Code 102

**Possible Parents**

#### Description

The server send us a list of 10 possible distributed parents to connect to. Messages of this type are sent to us at regular intervals, until we tell the server we don't need more possible parents with a HaveNoParent message.

#### Function Names

Museekd: SNetInfo  
Nicotine: PossibleParents

#### Data Order

  - Send
      - *No Message*
  - Receive *list of search parents*
    1.  **int** <ins>number of parents</ins>
    2.  Iterate for <ins>number of parents</ins>
        1.  **string** <ins>username</ins>
        2.  **ip** <ins>ip</ins>
        3.  **int** <ins>port</ins>

### Server Code 103

**Wishlist Search**

#### Function Names

Museekd: SWishlistSearch  
Nicotine: WishlistSearch

#### Description

#### Data Order

  - Send
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>search query</ins>
  - Receive
      - *No Message*

### Server Code 104

**Wishlist Interval**

#### Function Names

Museekd: SWishlistInterval  
Nicotine: WishlistInterval

#### Description

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **int** <ins>interval</ins>

### Server Code 110

**Get Similar Users**

#### Function Names

Museekd: SGetSimilarUsers  
Nicotine: SimilarUsers

#### Description

The server sends us a list of similar users related to our interests.

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **int** <ins>number of users</ins>
    2.  Iterate for <ins>number of user</ins>
        1.  **string** <ins>username</ins>
        2.  **int** <ins>status</ins>

### Server Code 111

**Get Item Recommendations**

#### Function Names

Museekd: SGetItemRecommendations  
Nicotine: ItemRecommendations

#### Description

The server sends us a list of recommendations related to a specific item, which is usually present in the like/dislike list or an existing recommendation list.

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
    1.  **string** <ins>item</ins>
    2.  **int** <ins>number of
        recommendations</ins><ins> </ins>
    3.  Iterate for <ins>number of
        recommendations</ins><ins> </ins>
        1.  **string** <ins>recommendation</ins>
        2.  **int** <ins>number of recommendations
            for this recommendation (can be negative)</ins>

### Server Code 112

**Get Item Similar Users**

#### Function Names

Museekd: SGetItemSimilarUsers  
Nicotine: ItemSimilarUsers

#### Description

The server sends us a list of similar users related to a specific item, which is usually present in the like/dislike list or recommendation list.

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
    1.  **string** <ins>item</ins>
    2.  **int** <ins>number of users</ins>
    3.  Iterate for <ins>number of user</ins>
        1.  **string** <ins>username</ins>
        2.  **int** 0

### Server Code 113

**Room Tickers**

#### Function Names

Museekd: SRoomTickers  
Nicotine: RoomTickerState

#### Description

The server returns a list of tickers in a chat room.

Tickers are customizable, user-specific messages that appear in a banner at the top of a chat room.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **int** <ins>number of users</ins>
    3.  Iterate for <ins>number of user</ins>
        1.  **string** <ins>username</ins>
        2.  **string** <ins>tickers</ins>

### Server Code 114

**Room Ticker Add**

#### Function Names

Museekd: SRoomTickerAdd  
Nicotine: RoomTickerAdd

#### Description

The server sends us a new ticker that was added to a chat room.

Tickers are customizable, user-specific messages that appear in a banner at the top of a chat room.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
    3.  **string** <ins>ticker</ins>

### Server Code 115

**Room Ticker Remove**

#### Function Names

Museekd: SRoomTickerRemove  
Nicotine: RoomTickerRemove

#### Description

The server informs us that a ticker was removed from a chat room.

Tickers are customizable, user-specific messages that appear in a banner at the top of a chat room.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>

### Server Code 116

**Set Room Ticker**

#### Function Names

Museekd: SSetRoomTicker  
Nicotine: RoomTickerSet

#### Description

We send this to the server when we change our own ticker in a chat room.

Tickers are customizable, user-specific messages that appear in a banner at the top of a chat room.

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>ticker</ins>
  - Receive
      - *No Message*

### Server Code 117

**Add Hated Interest**

#### Function Names

Museekd: SInterestHatedAdd  
Nicotine: AddThingIHate

#### Description

We send this to the server when we add an item to our hate list.

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 118

**Remove Hated Interest**

#### Function Names

Museekd: SInterestHatedRemove  
Nicotine: RemoveThingIHate

#### Description

We send this to the server when we remove an item from our hate list.

#### Data Order

  - Send
    1.  **string** <ins>item</ins>
  - Receive
      - *No Message*

### Server Code 120

**Room Search**

#### Function Names

Museekd: SRoomSearch  
Nicotine: RoomSearch

#### Description

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>ticket</ins>
    3.  **string** <ins>search query</ins>
  - Receive
      - *No Message*

### Server Code 121

**Send Upload Speed**

#### Function Names

Museekd: SSendUploadSpeed  
Nicotine: SendUploadSpeed

#### Description

We send this after a finished upload to let the server update the speed statistics for ourselves.

#### Data Order

  - Send *average upload transfer speed*
    1.  **int** <ins>speed</ins>
  - Receive
      - *No Message*

### Server Code 122

**User Privileges**

#### Function Names

Museekd: SUserPrivileges  
Nicotine: UserPrivileged

#### Description

We ask the server whether a user is privileged or not.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>username</ins>
    2.  **char** <ins>privileged</ins> (boolean
        internal to museekd)

### Server Code 123

**Give Privileges**

#### Function Names

Museekd: SGivePrivileges  
Nicotine: GivePrivileges

#### Description

We give (part of) our privileges, specified in days, to another user on the network.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **int** <ins>days</ins>
  - Receive
      - *No Message*

### Server Code 124

**Notify Privileges**

#### Function Names

Nicotine: NotifyPrivileges

#### Description

The server sends us a notification about our privileges.

#### Data Order

  - Send
    1.  **int** <ins>token</ins>
    2.  **string** <ins>username</ins>
  - Receive
    1.  **int** <ins>token</ins>
    2.  **string** <ins>username</ins>

### Server Code 125

**Acknowledge Privilege Notification**

#### Function Names

Nicotine: AckNotifyPrivileges

#### Description

#### Data Order

  - Send
    1.  **int** <ins>token</ins>
  - Receive
    1.  **int** <ins>token</ins>

### Server Code 126

**Branch Level**

#### Description

Tell the server what is our position in our branch (xth generation)

#### Function Names

Museekd: SBranchLevel  
Nicotine: Unimplemented

#### Data Order

  - Send
    1.  **int** <ins>branch\_level</ins>
  - Receive
      - *No Message*

### Server Code 127

**Branch Root**

#### Description

Tell the server the username of the root of the branch we're in

#### Function Names

Museekd: SBranchRoot  
Nicotine: Unimplemented

#### Data Order

  - Send
    1.  **string** <ins>branch\_root</ins>
  - Receive
      - *No Message*

### Server Code 129

**Child depth**

#### Description

Tell the server the maximum number of generation of children we have.

#### Function Names

Museekd: SChildDepth  
Nicotine: Unimplemented

#### Data Order

  - Send
    1.  **int** <ins>child\_depth</ins>
  - Receive
      - *No Message*

### Server Code 133

**Private Room Users**

#### Description

The server sends us a list of room users that we can alter (add operator abilities / dismember).

#### Function Names

Museekd: SPrivRoomAlterableMembers  
Nicotine: PrivateRoomUsers

#### Data Order

  - Send
    1.  *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **int** <ins>number of users</ins>
    3.  Iterate for <ins>number of users</ins>
        1.  **string** <ins>users</ins>

### Server Code 134

**Private Room Add User**

#### Description

We send this to inform the server that we've added a user to a private room.

#### Function Names

Museekd: SPrivRoomAddUser  
Nicotine: PrivateRoomAddUser

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>

### Server Code 135

**Private Room Remove User**

#### Description

We send this to inform the server that we've removed a user from a private room.

#### Function Names

Museekd: SPrivRoomRemoveUser  
Nicotine: PrivateRoomRemoveUser

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>

### Server Code 136

**Private Room Drop Membership**

#### Description

We send this to the server to remove our own membership of a private room.

#### Function Names

Museekd: SPrivRoomDismember  
Nicotine: PrivateRoomDismember

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
      - *No Message*

### Server Code 137

**Private Room Drop Ownership**

#### Description

We send this to the server to stop owning a private room.

#### Function Names

Museekd: SPrivRoomDisown  
Nicotine: PrivateRoomDisown

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
      - *No Message*

### Server Code 138

**Private Room Unknown**

#### Description

Unknown purporse

#### Function Names

Museekd: SPrivRoomUnknown138  
Nicotine: PrivateRoomSomething

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 139

**Private Room Added**

#### Description

The server sends us this message when we are added to a private room.

#### Function Names

Museekd: SPrivRoomAdded  
Nicotine: PrivateRoomAdded

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 140

**Private Room Removed**

#### Description

The server sends us this message when we are removed from a private room.

#### Function Names

Museekd: SPrivRoomRemoved  
Nicotine: PrivateRoomRemoved

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 141

**Private Room Toggle**

#### Description

We send this when we want to enable or disable invitations to private rooms.

#### Function Names

Museekd: SPrivRoomToggle  
Nicotine: PrivateRoomToggle

#### Data Order

  - Send
    1.  **bool** <ins>enable</ins>
  - Receive
    1.  **bool** <ins>enable</ins>

### Server Code 142

**New Password**

#### Description

We send this to the server to change our password. We receive a response if our password changes.

#### Function Names

Museekd: SNewPassword  
Nicotine: ChangePassword

#### Data Order

  - Send
    1.  **string** <ins>pass</ins>
  - Receive
    1.  **string** <ins>pass</ins>

### Server Code 143

**Private Room Add Operator**

#### Description

We send this to the server to add private room operator abilities to a user.

#### Function Names

Museekd: SPrivRoomAddOperator  
Nicotine: PrivateRoomAddOperator

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
    2.  **string** <ins>operator</ins>
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>operator</ins>

### Server Code 144

**Private Room Remove Operator**

#### Description

We send this to the server to remove private room operator abilities from a user.

#### Function Names

Museekd: SPrivRoomRemoveOperator  
Nicotine: PrivateRoomRemoveOperator

#### Data Order

  - Send
    1.  **string** <ins>room</ins>
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 145

**Private Room Operator Added**

#### Description

The server send us this message when we're given operator abilities in a private room.

#### Function Names

Museekd: SPrivRoomOperatorAdded  
Nicotine: PrivateRoomOperatorAdded

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 146

**Private Room Operator Removed**

#### Description

The server send us this message when our operator abilities are removed in a private room.

#### Function Names

Museekd: SPrivRoomOperatorRemoved  
Nicotine: PrivateRoomOperatorRemoved

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>

### Server Code 148

**Private Room Operators**

#### Description

The server sends us a list of operators in a specific room, that we can remove operator abilities from.

#### Function Names

Museekd: SPrivRoomAlterableOperators  
Nicotine: PrivateRoomOwned

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **int** <ins>number of operators in
        room</ins>
    3.  Iterate the <ins>number of operators</ins>
        **museekd uses a vector of strings**
        1.  **string** <ins>operator</ins>

### Server Code 149

**Message Users**

#### Description

Sends a broadcast private message to the given list of users.

#### Function Names

Museekd: SMessageUsers  
Nicotine: Unimplemented

#### Data Order

  - Send
    1.  **int** <ins>number of users</ins>
    2.  Iterate the <ins>number of users</ins>
        **museekd uses a vector of strings**
        1.  **string** <ins>username</ins>
    3.  **string** <ins>message</ins>
  - Receive
      - *No Message*

### Server Code 150

**Ask Public Chat**

#### Description

We ask the server to send us messages from all public rooms, also known as public chat.

#### Function Names

Museekd: SAskPublicChat  
Nicotine: JoinPublicRoom

#### Data Order

  - Send
      - Empty Message
  - Receive
      - *No Message*

### Server Code 151

**Stop Public Chat**

#### Description

We ask the server to stop sending us messages from all public rooms, also known as public chat.

#### Function Names

Museekd: SStopPublicChat  
Nicotine: LeavePublicRoom

#### Data Order

  - Send
      - Empty Message
  - Receive
      - *No Message*

### Server Code 152

**Public Chat Message**

#### Description

The server sends this when a new message has been written in a public room (every single line written in every public room).

#### Function Names

Museekd: SPublicChat  
Nicotine: PublicRoomMessage

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>
    2.  **string** <ins>username</ins>
    3.  **string** <ins>message</ins>

### Server Code 153

**Related Searches**

#### Description

**DEPRECATED ? (empty list from server as of 2018)**

The server returns a list of related search terms for a search query.

#### Function Names

Museekd: SRelatedSearch  
Nicotine: RelatedSearch

#### Data Order

  - Send
    1.  **string** <ins>query</ins>
  - Receive
    1.  **string** <ins>query</ins>
    2.  **int** <ins>number of terms</ins>
    3.  Iterate for <ins>number of term</ins>
        1.  **string** <ins>term</ins>
        2.  **int** <ins>score</ins>

### Server Code 1001

**Can't Connect To Peer**

#### Function Names

Museekd: SCannotConnect  
Nicotine: CantConnectToPeer

#### Description

**DEPRECATED. Since direct and indirect connection attempts are made simultaneously by the official client nowadays, it's not safe to send this message, as we can't be certain that both connection methods have been fully attempted. The order of the attempts is also unpredictable.**

We send this to say we can't connect to peer after it has asked us to connect. We receive this if we asked peer to connect and it can't do this. This message means a connection can't be established either way.

See also: [Peer Connection Message Order](#peer-connection-message-order)

#### Data Order

  - Send *to the Server if we cannot connect to a peer.*
    1.  **int** <ins>token</ins>
    2.  **string** <ins>username</ins>
  - Receive *this response means we are both firewalled or otherwise
    unable to connect to each other.*
    1.  **int** <ins>token</ins>
    2.  **string** <ins>username</ins>

### Server Code 1003

**Can't Create Room**

#### Function Names

Museekd: Unimplemented  
Nicotine: CantCreateRoom

#### Description

Server tells us a new room cannot be created. This message only seems to be sent if you try to create a room with the same name as an existing private room. In other cases, such as using a room name with leading or trailing spaces, only a private message containing an error message is sent.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>room</ins>

# Peer Messages

| Send         | Receive           |
| ------------ | ----------------- |
| Send to Peer | Receive from Peer |

In museekd 0.1.13, these messages are sent and received in
Museek/PeerConnection.cc and defined in Museek/PeerMessages.hh. Since
museekd 0.2, they are defined in museekd/peermessages.h.

In Nicotine, these messages are matched to their message number in slskproto.py in the SlskProtoThread function, defined in slskmessages.py and callbacks for the messages are set in pynicotine.py.

#### The Peer Init Message format

| Message Length | Code   | Message Contents |
| -------------- | ------ | ---------------- |
| 4 Bytes        | 1 Byte | ...              |

#### Peer Init Message Index

| Code | Message                         |
| ---- | ------------------------------- |
| 0    | [Pierce Firewall](#peer-code-0) |
| 1    | [Peer Init](#peer-code-1)       |

### Peer Connection Message Order

1.  User A sends a [Peer Init](#peer-code-1) to User B.  
If this succeeds, a connection is established, and we're free to send peer messages.  
If this fails (socket cannot connect), we proceed with an indirect connection request (step 2).
2.  User A sends [ConnectToPeer](#server-code-18) to the Server with a unique token
3.  The Server sends a [ConnectToPeer](#server-code-18) response to User B with the same token
4.  User B sends a [Pierce Firewall](#peer-code-0) to User A with the same token.  
If this succeeds, a connection is established, and User A sends the original [Peer Init](#peer-code-1).  
If this fails, there's no way to establish a connection. User B used to proceed with step 5, but this is no longer the case in modern clients.
5.  User B sends a [Cannot Connect](#server-code-1001) to the Server (**DEPRECATED**, see [Can't Connect To Peer](#server-code-1001))
6.  The Server sends a [Cannot Connect](#server-code-1001) response to User A

### Peer Code 0

**Pierce Firewall**

#### Function Names

Nicotine: PierceFireWall

#### Description

This is the very first message sent by the peer that established a connection, if it has been asked by the other peer to do so. The token is taken from the ConnectToPeer server message.

See also: [Peer Connection Message
Order](#peer-connection-message-order)

#### Data Order

  - Send
      - **uint32** <ins>token</ins> *Unique Number*
  - Receive
      - **uint32** <ins>token</ins> *Unique Number*

### Peer Code 1

**Peer Init**

#### Function Names

Nicotine: PeerInit

#### Description

This message is sent by the peer that initiated a connection, not necessarily a peer that actually established it. Token apparently can be anything. Type is 'P' if it's anything but filetransfer, 'F' otherwise.

See also: [Peer Connection Message
Order](#peer-connection-message-order)

#### Data Order

  - Send
      - **string** <ins>username</ins> *Local Username*
      - **string** <ins>type</ins> *Connection Type
        (P, F or D)*
      - **uint32** <ins>token</ins> *Unique Number*
  - Receive
      - **string** <ins>username</ins> *Remote Username*
      - **string** <ins>type</ins> *Connection Type
        (P, F or D)*
      - **uint32** <ins>token</ins> *Unique Number*

#### The Message format

| Message Length | Code    | Message Contents |
| -------------- | ------- | ---------------- |
| 4 Bytes        | 4 Bytes | ...              |

#### Message Index

| Code | Message                                    |
| ---- | ------------------------------------------ |
| 4    | [Shares Request](#peer-code-4)             |
| 5    | [Shares Reply](#peer-code-5)               |
| 8    | [Search Request](#peer-code-8)             |
| 9    | [Search Reply](#peer-code-9)               |
| 15   | [User Info Request](#peer-code-15)         |
| 16   | [User Info Reply](#peer-code-16)           |
| 36   | [Folder Contents Request](#peer-code-36)   |
| 37   | [Folder Contents Reply](#peer-code-37)     |
| 40   | [Transfer Request](#peer-code-40)          |
| 41   | [Upload Reply](#peer-code-41-a)            |
| 41   | [Download Reply](#peer-code-41-b)          |
| 41   | [Transfer Reply](#peer-code-41-c)          |
| 42   | [Upload Placehold](#peer-code-42)          |
| 43   | [Queue Download](#peer-code-43)            |
| 44   | [Upload Queue Notification](#peer-code-44) |
| 46   | [Upload Failed](#peer-code-46)             |
| 50   | [Queue Failed](#peer-code-50)              |
| 51   | [Place In Queue Request](#peer-code-51)    |
| 52   | [Upload Queue Notification](#peer-code-52) |

### Peer Code 4

**Shares Request**

#### Function Names

Museekd: PSharesRequest  
Nicotine: GetShareFileList

#### Description

We send this to a peer to ask for a list of shared files.

#### Data Order

  - Send
      - Empty Message
  - Receive
      - Empty Message

### Peer Code 5

**Shares Reply**

#### Function Names

Museekd: PSharesReply  
Nicotine: SharedFileList

#### Description

A peer responds with a list of shared files when we've sent a GetSharedFileList.

#### Data Order

  - Send *shares database*
    1.  Iterate thru shares database
        1.  **data**
  - Receive *shares database*
    1.  decompress
    2.  **int** <ins>number of directories</ins>
    3.  Iterate <ins>number of directories</ins>
        1.  **string** <ins>directory</ins>
        2.  **int** <ins>number of files</ins>
        3.  Iterate <ins>number of files</ins>
            1.  **char** ??? (unused)
            2.  **string** <ins>filename</ins>
            3.  **off\_t** <ins>size</ins> *File
                size*
            4.  **string** <ins>ext</ins>
                *Extentsion*
            5.  **int** <ins>number of
                attributes</ins>
            6.  Iterate <ins>number of
                attributes</ins>
                1.  **int** <ins>place in
                    attributes</ins> (unused by museekd)
                2.  **int** <ins>attribute</ins>

### Peer Code 8

**Search Request**

#### Function Names

Museekd: PSearchRequest  
Nicotine: FileSearchRequest

#### Description

We send this to the peer when we search for a file. Alternatively, the peer sends this to tell us it is searching for a file.

#### Data Order

  - Send
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>query</ins>
  - Receive
    1.  **int** <ins>ticket</ins>
    2.  **string** <ins>query</ins>

### Peer Code 9

**Search Reply**

#### Function Names

Museekd: PSearchReply  
Nicotine: FileSearchResult

#### Description

The peer sends this when it has a file search match. The token/ticket is taken from original FileSearchRequest message.

#### Data Order

  - Send
    1.  **string** <ins>username</ins>
    2.  **int** <ins>ticket</ins>
    3.  **int** <ins>results size</ins> *number of
        results*
    4.  Iterate for number of results
        1.  **uchar** 1
        2.  **string** <ins>filename</ins>
        3.  **off\_t** <ins>size</ins>
        4.  **string** <ins>ext</ins>
        5.  **int** <ins>attribute size</ins>
        6.  Iterate <ins>number of attributes</ins>
            1.  **int** <ins>place in
                attributes</ins>
            2.  **int** <ins>attribute</ins>
    5.  **bool** <ins>slotfree</ins>
    6.  **int** <ins>avgspeed</ins>
    7.  **off\_t** <ins>queue length</ins>
  - Receive
    1.  decompress
    2.  **string** <ins>username</ins>
    3.  **int** <ins>ticket</ins>
    4.  **int** <ins>results size</ins>
        <ins>number of results</ins>
    5.  Iterate for <ins>number of results</ins>
        museekd pop buffer
        1.  **string** <ins>filename</ins>
        2.  **off\_t** <ins>size</ins>
        3.  **string** <ins>ext</ins>
        4.  **int** <ins>number of attributes</ins>
        5.  Iterate <ins>number of attributes</ins>
            1.  **int** <ins>place in
                attributes</ins>
            2.  **int** <ins>attribute</ins>
    6.  **bool** <ins>slotfree</ins>
    7.  **int** <ins>avgspeed</ins>
    8.  **off\_t** <ins>queue length</ins>

### Peer Code 15

**User Info Request**

#### Function Names

Museekd: PInfoRequest  
Nicotine: UserInfoRequest

#### Description

We ask the other peer to send us their user information, picture and all.

#### Data Order

  - Send
      - Empty Message
  - Receive
      - Empty Message

### Peer Code 16

**User Info Reply**

#### Function Names

Museekd: PInfoReply  
Nicotine: UserInfoReply

#### Description

A peer responds with this when we've sent a UserInfoRequest.

#### Data Order

  - Send description, picture, totalupl, queuesize, slotfree
    1.  **string** <ins>description</ins>
    2.  Check contents of <ins>picture</ins>
          - If <ins>picture</ins> is not empty
            1.  **bool** <ins>has\_picture</ins> 1
            2.  **string** <ins>picture</ins>
          - If <ins>picture</ins> is empty
            1.  **bool** <ins>has\_picture</ins> 0
    3.  **uint** <ins>totalupl</ins>
    4.  **uint** <ins>queuesize</ins>
    5.  **bool** <ins>slotsfree</ins> *Can
        immediately upload*
  - Receive
    1.  **string** <ins>description</ins>
    2.  **char** <ins>has\_picture</ins>
    3.  Check contents of <ins>has\_picture</ins>
        1.  If <ins>has\_picture</ins> is not empty
            1.  **string** <ins>picture</ins>
    4.  **int** <ins>totalupl</ins>
    5.  **int** <ins>queuesize</ins>
    6.  **bool** <ins>slotsfree</ins> *Can
        immediately download*

### Peer Code 36

**Folder Contents Request**

#### Function Names

Museekd: PFolderContentsRequest  
Nicotine: FolderContentsRequest

#### Description

We ask the peer to send us the contents of a single folder.

#### Data Order

  - Send
    1.  **int** <ins>number of files in
        directory</ins>
    2.  Iterate <ins>number of files in
        directory</ins>
        1.  **string** <ins>file</ins>
  - Receive
    1.  **int** <ins>number of files in
        directory</ins>
    2.  Iterate <ins>number of files in
        directory</ins>
        1.  **string** <ins>file</ins>

### Peer Code 37

**Folder Contents Reply**

#### Function Names

Museekd: PFolderContentsReply  
Nicotine: FolderContentsResponse

#### Description

A peer responds with the contents of a particular folder (with all subfolders) when we've sent a FolderContentsRequest.

#### Data Order

  - Send
    1.  **int** <ins>number of folders</ins>
    2.  Iterate for <ins>number of folders</ins>
        1.  **string** <ins>dir</ins>
        2.  **int** <ins>number of files</ins>
        3.  Iterate <ins>number of files</ins>
            1.  **char** <ins>true</ins>
            2.  **string** <ins>file</ins>
            3.  **off\_t** <ins>size</ins>
            4.  **string** <ins>ext</ins> Extension
            5.  **int** <ins>number of
                attributes</ins>
                1.  **int** <ins>attribute
                    number</ins>
                2.  **int** <ins>attribute</ins>
  - Receive
    1.  decompress
    2.  **int** <ins>number of folders</ins>
    3.  Iterate for <ins>number of folders</ins>
        1.  **string** <ins>dir</ins>
        2.  **int** <ins>number of files</ins>
        3.  Iterate <ins>number of files</ins>
            1.  **char** <ins>???</ins> (unused)
            2.  **string** <ins>file</ins>
            3.  **off\_t** <ins>size</ins>
            4.  **string** <ins>ext</ins> Extension
            5.  **int** <ins>number of
                attributes</ins>
                1.  **int** <ins>attribute
                    number</ins>
                2.  **int** <ins>attribute</ins>

### Peer Code 40

**Transfer Request**

#### Function Names

Museekd: PTransferRequest  
Nicotine: TransferRequest

#### Description

We request a file from a peer, or tell a peer that we want to send a file to them.

#### Data Order

  - Send
    1.  **int** <ins>direction</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>filename</ins>
    4.  Check contents of <ins>direction</ins>
          - **off\_t** <ins>filesize</ins> *if
            direction == 1*
  - Receive
    1.  **int** <ins>direction</ins>
    2.  **int** <ins>ticket</ins>
    3.  **string** <ins>filename</ins>
    4.  Check contents of <ins>direction</ins>
          - **off\_t** <ins>filesize</ins> *if
            direction == 1*

### Peer Code 41 a

**Upload Reply**

#### Function Names

Museekd: PUploadReply  
Nicotine: TransferResponse

#### Description

Response to TransferRequest - either we (or the other peer) agrees, or tells the reason for rejecting the file transfer.

#### Data Order

  - Send
    1.  **string** <ins>ticket</ins>
    2.  **uchar** <ins>allowed</ins>
    3.  Check contents of <ins>allowed</ins>
          - **off\_t** <ins>filesize</ins> *if
            allowed == 1*
          - **string** <ins>reason</ins> *if allowed
            == 0*
  - Receive
      - *No Message*

### Peer Code 41 b

**Download Reply**

#### Function Names

Museekd: PDownloadReply  
Nicotine: TransferResponse

#### Description

Response to TransferRequest - either we (or the other peer) agrees, or tells the reason for rejecting the file transfer.

#### Data Order

  - Send
    1.  **string** <ins>ticket</ins>
    2.  **uchar** <ins>allowed</ins>
    3.  Check contents of <ins>allowed</ins>
          - **string** <ins>reason</ins> *if allowed
            == 0*
  - Receive
      - *No Message*

### Peer Code 41 c

**Transfer Reply**

#### Function Names

Museekd: PTransferReply  
Nicotine: TransferResponse

#### Description

Response to TransferRequest - either we (or the other peer) agrees, or tells the reason for rejecting the file transfer.

#### Data Order

  - Send
      - *No Message*
  - Receive
    1.  **string** <ins>ticket</ins>
    2.  **char** <ins>allowed</ins> == 1
    3.  Check contents of <ins>allowed</ins>
          - **off\_t** <ins>filesize</ins> *if
            allowed == 1*
          - **string** <ins>reason</ins> *if allowed
            == 0*

### Peer Code 42

**Upload Placehold**

#### Function Names

Museekd: PUploadPlacehold  
Nicotine: PlaceholdUpload

#### Description

**DEPRECATED**

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 43

**Queue Upload or Download**

#### Function Names

Museekd: PQueueDownload  
Nicotine: QueueUpload

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 44

**Place In Queue Reply**

#### Function Names

Museekd: PPlaceInQueueReply  
Nicotine: PlaceInQueue

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>place</ins>
  - Receive
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>place</ins>

### Peer Code 46

**Upload Failed**

#### Function Names

Museekd: PUploadFailed  
Nicotine: UploadFailed

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 50

**Queue Failed**

#### Function Names

Museekd: PQueueFailed  
Nicotine: QueueFailed

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>reason</ins>
  - Receive
    1.  **string** <ins>filename</ins>
    2.  **string** <ins>reason</ins>

### Peer Code 51

**Place In Queue Request**

#### Function Names

Museekd: PPlaceInQueueRequest  
Nicotine: PlaceInQueueRequest

#### Description

#### Data Order

  - Send
    1.  **string** <ins>filename</ins>
  - Receive
    1.  **string** <ins>filename</ins>

### Peer Code 52

**Upload Queue Notification**

#### Function Names

Museekd: PUploadQueueNotification  
Nicotine: UploadQueueNotification

#### Description

#### Data Order

  - Send
      - Empty Message
  - Receive
      - Empty Message

# Distributed Messages

| Send    | Send to Node      |
| ------- | ----------------- |
| Receive | Receive from Node |

In museekd 0.1.13, these messages are sent and received in
Museek/DistribConnection.cc and defined in Museek/DistribMessages.hh.
Since museekd 0.2, they are defined in museekd/distributedmessages.h.

In Nicotine, these messages are matched to their message number in slskproto.py in the SlskProtoThread function, defined in slskmessages.py and callbacks for the messages are set in pynicotine.py.

#### The Message format

| Message Length | Code   | Message Contents |
| -------------- | ------ | ---------------- |
| 4 Bytes        | 1 Byte | ...              |

#### Message Index

| Code | Message                                      |
| ---- | -------------------------------------------- |
| 0    | [Ping](#distributed-code-0)                  |
| 3    | [Search Request](#distributed-code-3)        |
| 4    | [Branch Level](#distributed-code-4)          |
| 5    | [Branch Root](#distributed-code-5)           |
| 7    | [Child Depth](#distributed-code-7)           |
| 93   | [Server Search Request](#distributed-code-93)|

### Distributed Code 0

**Ping**

#### Description

Send it every 60 sec.

#### Function Names

Museekd: DPing  
Nicotine: DistribAlive

#### Data Order

  - Send
      - Empty Message
  - Receive
    1.  **uint32** <ins>unknown</ins>

### Distributed Code 3

**Search Request**

#### Description

Search request that arrives through the distributed network. 
We transmit the search request to our children.

Search requests are sent to us by the server using SearchRequest if we're a branch root, or by our parent using DistribSearch.

#### Function Names

Museekd: DSearchRequest  
Nicotine: DistribSearch

#### Data Order

  - Send
    1.  **int** <ins>unknown</ins>
    2.  **string** <ins>username</ins>
    3.  **int** <ins>ticket</ins>
    4.  **string** <ins>query</ins>
  - Receive
    1.  **int** <ins>unknown</ins>
    2.  **string** <ins>username</ins>
    3.  **int** <ins>ticket</ins>
    4.  **string** <ins>query</ins>

### Distributed Code 4

**Branch Level**

#### Description

See SBranchLevel

#### Function Names

Museekd: DBranchLevel  
Nicotine: Unimplemented

#### Data Order

  - Send
    1.  **uint32** <ins>branch\_level</ins>
  - Receive
    1.  **uint32** <ins>branch\_level</ins>

### Distributed Code 5

**Branch Root**

#### Description

See SBranchRoot

#### Function Names

Museekd: DBranchRoot  
Nicotine: Unimplemented

#### Data Order

  - Send
    1.  **string** <ins>branch\_root</ins>
  - Receive
    1.  **string** <ins>branch\_root</ins>

### Distributed Code 7

**Branch Level**

#### Description

See SChildDepth

#### Function Names

Museekd: DChildDepth  
Nicotine: Unimplemented

#### Data Order

  - Send
    1.  **uint32** <ins>child\_depth</ins>
  - Receive
    1.  **uint32** <ins>child\_depth</ins>

### Distributed Code 93

**Server Search Request**

#### Description

Search request that arrives through the distributed network. 
We transmit the search request to our children.

Search requests are sent to us by the server using SearchRequest if we're a branch root, or by our parent using DistribSearch.

#### Function Names

Museekd: Unimplemented  
Nicotine: DistribServerSearch

#### Data Order

  - Send
    1.  **off_t** <ins>unknown</ins> *always 210503729152 (?)*
    2.  **string** <ins>username</ins>
    3.  **int** <ins>ticket</ins>
    4.  **string** <ins>query</ins>
  - Receive
    1.  **off_t** <ins>unknown</ins> *always 210503729152 (?)*
    2.  **string** <ins>username</ins>
    3.  **int** <ins>ticket</ins>
    4.  **string** <ins>query</ins>

# Museek Data Types

### StringMap

  - std::map\<std::string, std::string\>

### StringList

  - std::vector\<std::string\>

### WStringList

  - std::vector\<std::wstring\> WStringList

### WTickers

  - std::map\<std::string, std::wstring\>

### Recommendations, SimilarUsers, RoomList

  - std::map\<std::string, uint32\>

### NetInfo

  - std::map\<std::string, std::pair\<std::string, uint32\> \>

### UserData

1.  **uint32** <ins>status</ins> *Online Status*
2.  **uint32** <ins>avgspeed</ins> *Average Speed*
3.  **uint32** <ins>downloadnum</ins> *Number of
    downloaded files*
4.  **uint32** <ins>files</ins> *Files shared*
5.  **uint32** <ins>dirs</ins> *Directories shared*
6.  **bool** <ins>slotsfree</ins> *Slots free*

### RoomData

  - std::map\<std::string, UserData\>

### Folder

  - std::map\<std::string, FileEntry\>

### Shares

  - std::map\<std::string, Folder\>

### WFolder

  - std::map\<std::wstring, FileEntry\>

### Folders

  - std::map\<std::string, Shares\>

### WShares

  - std::map\<std::wstring, WFolder\>

### WFolders

  - std::map\<std::wstring, WShares\>

### off\_t

  - Packed as a 64bit Integer
