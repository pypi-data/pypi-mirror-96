12.3.0
  - added credit account property
  - added feature to unsubscribe from market data (remove symbol from market watch)
  - removed maximum reliability value
  - fixed synchronization throttling

12.2.0
  - added retryOpts option to configure retries of certain REST/RPC requests upon failure
  - improved socket connection reliability
  - added CopyFactory code example

12.1.1
  - fixed abstract methods of HistoryStorage class

12.1.0
  - add name and login to account information
  - add a feature to select trade scaling mode in CopyFactory (i.e. if we want the trade size to be preserved or scaled according to balance when copying)

12.0.5
  - remove timers
  
12.0.4
  - fix is_synchronized check

12.0.3
  - fix subscribe_to_market_data API contract

12.0.1
  - added API to retrieve CopyFactory slave trading log
  - fixed race condition when orders are being added and completed fast
  - breaking change: changed signatures of SynchronizationListener methods
  - add reliability field
  - fixed async http requests
  - fixed conversion of time fields in packets
  - add symbol mapping setting to CopyFactory
  - fix quote health check logic
  - fixed concurrent account socket connections

11.0.0
  - breaking change: MetaApi options are now specified via an object
  - breaking change: CopyFactory options are now specified via an object
  - added traffic logger
  - added close by order support
  - added stop limit order support
  - bugfix MetatraderAccount.connect method to throw an error to avoid creating broken connections
  - add marginMode, tradeAllowed, investorMode fields to account information
  - breaking change: wait_synchronized to synchronize CopyFactory and RPC applications by default
  - improvements to position profit and account equity tracking on client side
  - real-time updates for margin fields in account information
  - breaking change: uptime now returns uptime measurements over several timeframes (1h, 1d, 1w)
  - do not retry synchronization after MetaApiConnection is closed
  - added option for reverse copying in CopyFactory API
  - added ConnectionHealthMonitor.server_health_status API to retrieve health status of server-side applications
  - added option to specify account-wide stopout and risk limits in CopyFactory API
  - track MetaApi application latencies
  - send RPC requests via RPC application
  - increased synchronization stability
  - added extensions for accounts
  - added metadata field for accounts to store extra information together with account

10.1.0
  - added support for portfolio strategies (i.e. the strategies which include several other member strategies) to CopyFactory API

10.0.1
  - bugfix health monitor

10.0.0
  - added incoming commissions to CopyFactory history API
  - breaking change: refactored reset_stopout method in CopyFactory trading API. Changed method name, added strategy_id parameter.
  - retry synchronization if synchronization attempt have failed
  - restore market data subscriptions on successful synchronization
  - added capability to monitor terminal connection health and measure terminal connection uptime
  - change packet orderer timeout from 10 seconds to 1 minute to accommodate for slower connections

9.1.0
  - added API to register MetaTrader demo accounts
  - fixed packet orderer to do not cause unnecessary resynchronization

9.0.0
  - added contractSize field to MetatraderSymbolSpecification model
  - added quoteSessions and tradeSessions to MetatraderSymbolSpecification model
  - added more fields to MetatraderSymbolSpecification model
  - breaking change: add on_positions_replaced and on_order_replaced events into SynchronizationListener and no longer invoke on_position_updated and on_order_updated during initial synchronization
  - removed excessive log message from subscribe API
  - breaking change: introduced synchronizationStarted event to increase synchronization stability
  - fixed wrong expected sequence number of synchronization packet in the log message
  - added positionId field to CopyFactoryTransaction model
  
8.0.2
  - added application setting to MetaApi class to make it possible to launch several 
  MetaApi applications in parallel on the same account
  - added time fields in broker timezone to objects
  - added time fields to MetatraderSymbolPrice model
  - fix simultaneous multiple file writes by one connection
  - now only one MetaApiConnection can be created per account at the same time to avoid history storage errors
  - added quoteStreamingIntervalInSeconds field to account to configure quote streaming interval
  - fixes to setup keywords
  - added CopyFactory trade-copying API
  - added latency and slippage metrics to CopyFactory trade copying API
  - added CopyFactory configuration client method retrieving active resynchronization tasks
  - improved description of CopyFactory account resynchronizing in readme
  - made it possible to use MetaApi class in interaction tests
  - breaking change: removed the `timeConverter` field from the account, replaced it with `brokerTimezone` and `brokerDSTSwitchTimezone` fields in the provisioning profile instead
  - added originalComment and clientId fields to MetatraderPosition
  - fixed occasional fake synchronization timeouts in waitSynchronized method
  - breaking change: changed API contract of MetaApiConnection.wait_synchronized method
  - added tags for MetaApi accounts
  - minor adjustments to equity calculation algorithm
  - added method to wait for active resynchronization tasks are completed in configuration CopyFactory api
  - added the ability to set the start time for synchronization, used for tests
  - resynchronize on lost synchronization packet to ensure local terminal state consistency
  
6.1.0
  - added ability to select filling mode when placing a market order, in trade options
  - added ability to set expiration options when placing a pending order, in trade options
  - added reason field to position, order and deal
  - added fillingMode field to MetaTraderOrder model
  - added order expiration time and type
  
6.0.2
  - added code sample download video to readme
  
6.0.1
  - update readme.md

6.0.0
  - breaking change: moved comment and clientId arguments from MetaApiConnection trade methods to options argument
  - added magic trade option to let you specify distinct magic number (expert advisor id) on each trade
  - added manualTrades field to account model so that it is possible to configure if MetaApi should place manual trades on the account
  - prepare MetatraderAccountApi class for upcoming breaking change in the API
  - added pagination and more filters to getAccounts API
  - added slippage option to trades
  - breaking change: rename close_position_by_symbol -> close_position**s**_by_symbol
  - added fillingModes to symbol specification
  - added executionMode to symbol specification
  - added logic to throw an exception if streaming API is invoked in automatic synchronization mode
  - added code samples for created account
  - save history on disk

4.0.0
  - add fields to trade result to match upcoming MetaApi contract
  - breaking change: throw TradeException in case of trade error
  - rename trade response fields so that they are more meaningful

3.0.0
  - improved account connection stability
  - added platform field to MetatraderAccountInformation model
  - breaking change: changed synchronize and waitSynchronized API to allow for unique synchronization id to be able to track when the synchronization is complete in situation when other clients have also requested a concurrent synchronization on the account
  - breaking change: changed default wait interval to 1s in wait* methods
2.0.0
  - breaking change: removed volume as an argument from a modifyOrder function
  - mark account as disconnected if there is no status notification for a long time
  - increased websocket client stability
  - added websocket and http client timeouts
  - improved account connection stability
1.1.4
  - increased synchronization speed
  - fixed connection stability issue during initial synchronization
1.1.3
  - initial release, version is set to be in sync with other SDKs