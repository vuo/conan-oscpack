#include <stdio.h>
#include <oscpack/osc/OscOutboundPacketStream.h>

int main()
{
	char buffer[1024];
	osc::OutboundPacketStream p(buffer, 1024);

	p << osc::BeginBundleImmediate
		<< osc::BeginMessage( "/test1" )
			<< true << 23 << (float)3.1415 << "hello" << osc::EndMessage
		<< osc::BeginMessage( "/test2" )
			<< true << 24 << (float)10.8 << "world" << osc::EndMessage
		<< osc::EndBundle;

	if (p.Size() != 88)
	{
		fprintf(stderr, "Error initializing oscpack.  Message data size %ld.\n", p.Size());
		return -1;
	}

	printf("Successfully initialized oscpack.  Message data size %ld.\n", p.Size());
	return 0;
}
