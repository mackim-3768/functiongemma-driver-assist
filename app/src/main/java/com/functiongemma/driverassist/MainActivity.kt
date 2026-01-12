package com.functiongemma.driverassist

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    DriverAssistScreen()
                }
            }
        }
    }
}

@Composable
private fun DriverAssistScreen() {
    var prompt by remember { mutableStateOf("차선 이탈이 감지됐어") }
    var outputJson by remember { mutableStateOf("[]") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(text = "FunctionGemma Driver Assist (Demo)", style = MaterialTheme.typography.titleLarge)

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = {
                prompt = "차선 이탈이 감지됐고 운전자가 핸들을 잡지 않았어"
            }) {
                Text("차선 이탈")
            }
            Button(onClick = {
                prompt = "졸음 운전이 의심돼"
            }) {
                Text("졸음")
            }
            Button(onClick = {
                prompt = "전방 충돌 위험이 높아"
            }) {
                Text("전방 충돌")
            }
        }

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(text = "Prompt")
            BasicTextField(
                value = prompt,
                onValueChange = { prompt = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                textStyle = TextStyle(color = MaterialTheme.colorScheme.onBackground)
            )
            Button(onClick = {
                outputJson = "[{\"name\":\"log_safety_event\",\"arguments\":{\"message\":\"stub\"}}]"
            }) {
                Text("Run")
            }
        }

        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(text = "Engineer Mode Output (JSON)")
            Text(text = outputJson, style = MaterialTheme.typography.bodySmall)
        }
    }
}
